import dnslib.server
import os
import logging
from dnslib import RR, RCODE, DNSRecord
from .common import Common

logger = logging.getLogger(__name__)

class DockerDNSResolverClass():
    def startThread():
        DockerDNSResolverClass.dnsPort = int(os.environ.get("DNS_PORT", 53))
        DockerDNSResolverClass.prepareLocalDomain()

        logger.info("started DNS server on port {}".format(DockerDNSResolverClass.dnsPort))        
        DockerDNSResolverClass.DNSlogger = dnslib.server.DNSLogger(prefix=False, logf=logger.debug)
        DockerDNSResolverClass.dockerResolverObj = DockerDNSResolverClass.DockerResolver()
        
        DockerDNSResolverClass.upstreamDNS = os.environ.get("DNS_UPSTREAM_HOST","8.8.8.8")
        DockerDNSResolverClass.upstreamDNSPort = int(os.environ.get("DNS_UPSTREAM_PORT",53))
        DockerDNSResolverClass.ProxyDNSRequests = False if os.environ.get("ENABLE_DNS_PROXY", "false").lower == "false" else True
        
        if DockerDNSResolverClass.ProxyDNSRequests:
            logger.info("Proxying unresolvable DNS requests to: {}/{}".format(DockerDNSResolverClass.upstreamDNS, DockerDNSResolverClass.upstreamDNSPort))

        DockerDNSResolverClass.dnsServer = dnslib.server.DNSServer(resolver=DockerDNSResolverClass.dockerResolverObj, port=DockerDNSResolverClass.dnsPort, logger=DockerDNSResolverClass.DNSlogger)
        DockerDNSResolverClass.dnsServer.start_thread()

    
    def prepareLocalDomain():
        DockerDNSResolverClass.localDomain = os.environ.get("LOCAL_DOMAIN","vpn.local")
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
                        for l in q.qname.label:
                            qLabelDecoded.append(l.decode("UTF-8"))
                        
                        qLabelReverse = qLabelDecoded.copy()
                        qLabelReverse.reverse()
                        domainComparePart = qLabelReverse[0:DockerDNSResolverClass.reverseLocalDomainSplitLength]
                        logger.debug("reverse labels: {} ".format(qLabelReverse))
                        logger.debug("domain compare part: {} ".format(domainComparePart))
                        logger.debug("localDomainSplit: {} ".format(DockerDNSResolverClass.reverseLocalDomainSplit))
                                
                        if domainComparePart  == DockerDNSResolverClass.reverseLocalDomainSplit:
                            compareString = "/" + qLabelDecoded[0]
                            logger.debug("comparing {} against {} entries in Common/entries".format(compareString,len(Common.entries)))
                            for e in Common.entries:
                                try:
                                    if e["name"] == compareString or compareString == "/*":
                                        for ip in e["ips"]:
                                            reply.add_answer(*RR.fromZone("{}.{}. 5 A {}".format(str(e["name"][1:]),DockerDNSResolverClass.localDomain,ip)))
                                            found = True
                                            
                                except Exception as err2:
                                    logger.error("Error processing docker entry {} - {}".format(e["name"],err2))
                                    
                except Exception as err:
                    logger.error("Error processing questions in DNS request! - {}".format(err))

            if found is False:
                if DockerDNSResolverClass.ProxyDNSRequests:
                    try:
                        proxy_req = dnsRequest.send(DockerDNSResolverClass.upstreamDNS,DockerDNSResolverClass.upstreamDNSPort)
                        reply = DNSRecord.parse(proxy_req)
                    except:
                        reply.header.rcode = RCODE.NXDOMAIN
                else:
                    reply.header.rcode = RCODE.NXDOMAIN
                    
            return reply



