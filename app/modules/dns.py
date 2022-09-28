import dnslib.server
import os
import logging
import sys
from dnslib import RR, RCODE, DNSRecord
from .common import Common

logger = logging.getLogger(__name__)


class DockerDNSResolverClass():
    upstreamDNSes = []
    dnsPort: int = 53
    DNSlogger: dnslib.server.DNSLogger = None
    dockerResolverObj: dnslib.server.BaseResolver = None
    ProxyDNSRequests: bool = False
    dnsServer: dnslib.server.DNSServer = None
    localDomain: str = ""
    localDomainSplit = []
    reverseLocalDomainSplit = []
    reverseLocalDomainSplitLength: int = -1
    
    def startThread():
        DockerDNSResolverClass.dnsPort = int(os.environ.get("DNS_PORT", 53))
        DockerDNSResolverClass.prepareLocalDomain()

        logger.info("started DNS server on port {}".format(DockerDNSResolverClass.dnsPort))
        DockerDNSResolverClass.DNSlogger = dnslib.server.DNSLogger(prefix=False, logf=logger.debug)
        DockerDNSResolverClass.dockerResolverObj = DockerDNSResolverClass.DockerResolver()
        DockerDNSResolverClass.ProxyDNSRequests = False if os.environ.get("ENABLE_DNS_PROXY", "false").lower() == "false" else True

        if DockerDNSResolverClass.ProxyDNSRequests:
            logger.info("Proxying unresolvable DNS requests to:")
            DockerDNSResolverClass.upstreamDNSes = []
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
                DockerDNSResolverClass.upstreamDNSes.append(dnsObject)
                logger.info("Added new DNS upstream entry:{}/{}".format(dnsObject["server"], dnsObject["port"]))
                
            if len(DockerDNSResolverClass.upstreamDNSes) <= 0:
                logger.error("Cannot proxy DNS requests as there are no defined servers!")
                sys.exit(5)

        DockerDNSResolverClass.dnsServer = dnslib.server.DNSServer(resolver=DockerDNSResolverClass.dockerResolverObj, port=DockerDNSResolverClass.dnsPort, logger=DockerDNSResolverClass.DNSlogger)
        DockerDNSResolverClass.dnsServer.start_thread()
    
    def prepareLocalDomain():
        DockerDNSResolverClass.localDomain = os.environ.get("LOCAL_DOMAIN", "vpn.local")
        DockerDNSResolverClass.localDomainSplit = DockerDNSResolverClass.localDomain.split(".")
        DockerDNSResolverClass.reverseLocalDomainSplit = DockerDNSResolverClass.localDomainSplit.copy()
        DockerDNSResolverClass.reverseLocalDomainSplit.reverse()
        DockerDNSResolverClass.reverseLocalDomainSplitLength = len(DockerDNSResolverClass.reverseLocalDomainSplit)

    class DockerResolver(dnslib.server.BaseResolver):
        def resolve(self, dnsRequest, handler):
            reply = dnsRequest.reply()
            found = False
            for q in dnsRequest.questions:
                try:
                    if len(q.qname.label) >= (len(DockerDNSResolverClass.localDomainSplit) + 1):
                        
                        qLabelDecoded = []
                        for labelName in q.qname.label:
                            qLabelDecoded.append(labelName.decode("UTF-8"))
                        
                        qLabelReverse = qLabelDecoded.copy()
                        qLabelReverse.reverse()
                        domainComparePart = qLabelReverse[0:DockerDNSResolverClass.reverseLocalDomainSplitLength]
                        logger.debug("reverse labels: {} ".format(qLabelReverse))
                        logger.debug("domain compare part: {} ".format(domainComparePart))
                        logger.debug("localDomainSplit: {} ".format(DockerDNSResolverClass.reverseLocalDomainSplit))
                                
                        if domainComparePart == DockerDNSResolverClass.reverseLocalDomainSplit:
                            compareString = "/" + qLabelDecoded[0]
                            logger.debug("comparing {} against {} entries in Common/entries".format(compareString, len(Common.entries)))
                            for e in Common.entries:
                                try:
                                    if e["name"] == compareString or compareString == "/*":
                                        for ip in e["ips"]:
                                            reply.add_answer(*RR.fromZone("{}.{}. 5 A {}".format(str(e["name"][1:]), DockerDNSResolverClass.localDomain, ip)))
                                            found = True
                                            
                                except Exception as err2:
                                    logger.error("Error processing docker entry {} - {}".format(e["name"], err2))

                except Exception as err:
                    logger.error("Error processing questions in DNS request! - {}".format(err))

            if found is False:
                if DockerDNSResolverClass.ProxyDNSRequests:
                    for attempt in DockerDNSResolverClass.upstreamDNSes:
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
