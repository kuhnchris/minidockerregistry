from app.modules.common import logger, common
from app.modules.interfaces.services import CommonServiceInterface
from dnslib import RR, RCODE, DNSRecord
import dnslib.server
import os


class DNSServerService(CommonServiceInterface):
    def __init__(self) -> None:
        super().__init__()
        self.ProxyDNSRequests = False if os.environ.get("ENABLE_DNS_PROXY", "false").lower() == "false" else True
        self.DNSPort = int(os.environ.get("DNS_PORT", 53))

        self.DNSLogger = dnslib.server.DNSLogger(prefix=False, logf=logger.debug)
        self.DNSResolver = DNSServerService.ContainerNameResolver()
        self.upstreamDNSes = []

        self.localDomain = ""
        self.localDomainSplit = []
        self.reverseLocalDomainSplit = []
        self.reverseLocalDomainSplitLength: int = -1
    
        if self.ProxyDNSRequests:
            logger.info("Proxying unresolvable DNS requests to:")
            for dnsServer in os.environ.get("DNS_UPSTREAM_HOST", "8.8.8.8").split(";"):
                dnsSplit = dnsServer.split(":")
                if len(dnsSplit) > 1:
                    dnsPort = int(dnsSplit[1])
                else:
                    dnsPort = 53

                dnsObject = {
                    "port": dnsPort,
                    "server": dnsSplit[0]
                }
                self.upstreamDNSes.append(dnsObject)
                logger.info("Added new DNS upstream entry:{}/{}".format(dnsObject["server"], dnsObject["port"]))
                
            if len(self.upstreamDNSes) <= 0:
                logger.error("Cannot proxy DNS requests as there are no defined servers!")
                raise ValueError

        self.prepareLocalDomain()

    def startService(self):
        self.startThread()

    def startThread(self):
        logger.info("started DNS server on port {}".format(self.dnsPort))
        self.dnsServer = dnslib.server.DNSServer(resolver=self.DNSResolver, port=self.DNSPort, logger=self.DNSLogger)
        self.dnsServer.start_thread()
    
    def prepareLocalDomain(self):
        self.localDomain = os.environ.get("LOCAL_DOMAIN", "vpn.local")
        self.localDomainSplit = self.localDomain.split(".")
        self.reverseLocalDomainSplit = self.localDomainSplit.copy()
        self.reverseLocalDomainSplit.reverse()
        self.reverseLocalDomainSplitLength = len(self.reverseLocalDomainSplit)

    class ContainerNameResolver(dnslib.server.BaseResolver):
        def __init__(self, service) -> None:
            super().__init__()
            self.service = service

        def resolve(self, dnsRequest, handler):
            reply = dnsRequest.reply()
            found = False
            for q in dnsRequest.questions:
                try:
                    if len(q.qname.label) >= (len(self.service.localDomainSplit) + 1):
                        
                        qLabelDecoded = []
                        for labelName in q.qname.label:
                            qLabelDecoded.append(labelName.decode("UTF-8"))
                        
                        qLabelReverse = qLabelDecoded.copy()
                        qLabelReverse.reverse()
                        domainComparePart = qLabelReverse[0:self.service.reverseLocalDomainSplitLength]
                        logger.debug("reverse labels: {} ".format(qLabelReverse))
                        logger.debug("domain compare part: {} ".format(domainComparePart))
                        logger.debug("localDomainSplit: {} ".format(self.service.reverseLocalDomainSplit))
                                
                        if domainComparePart == self.service.reverseLocalDomainSplit:
                            compareString = "/" + qLabelDecoded[0]
                            logger.debug("comparing {} against {} entries in Common/entries".format(compareString, len(common.container_data.containers)))
                            for e in common.container_data.containers:
                                try:
                                    if e.name == compareString or compareString == "/*":
                                        for ip in e.networks:
                                            reply.add_answer(*RR.fromZone("{}.{}. 5 A {}".format(str(e["name"][1:]), self.service.localDomain, ip)))
                                            found = True
                                            
                                except Exception as err2:
                                    logger.error("Error processing docker entry {} - {}".format(e["name"], err2))

                except Exception as err:
                    logger.error("Error processing questions in DNS request! - {}".format(err))

            if found is False:
                if self.service.ProxyDNSRequests:
                    for attempt in self.service.upstreamDNSes:
                        try:
                            proxy_req = dnsRequest.send(attempt["server"], attempt["port"])
                            reply = DNSRecord.parse(proxy_req)
                        except Exception as e:
                            logger.error("Upstream server {} caused exception: {}", attempt["server"], e)
                            reply.header.rcode = RCODE.NXDOMAIN
                        if reply.header.rcode != RCODE.NXDOMAIN:
                            break
                else:
                    reply.header.rcode = RCODE.NXDOMAIN
                    # reply.header.rcode = RCODE.NOTAUTH
                    # reply.header.rcode = RCODE.NOTZONE
                    
            return reply
