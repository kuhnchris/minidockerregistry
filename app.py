import hashlib
import logging
import docker
import dnslib.server
from dnslib import RR
from threading import Thread
from time import sleep
from flask import Flask, jsonify, render_template, request, redirect

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")
app = Flask(__name__, template_folder=".",
            static_url_path='/static/',
            static_folder='static/')

entries = []


def fetchDockerInfo():
    while True:
        logger.info("fetching Docker info...")
        try:
            client = docker.from_env()
            entries.clear()
            for c in client.containers():
                if c["State"] != "running":
                    continue
                entry = {"name": ", ".join(c["Names"]), "ips": [], "ports": [], "created": c["Created"]}
                networkSettings = c["NetworkSettings"]["Networks"]
                for k in networkSettings.keys():
                    ip = networkSettings[k]["IPAddress"]
                    entry["ips"].append(ip)

                for p in c["Ports"]:
                    if p["Type"] == "tcp":
                        prvPort = str(p["PrivatePort"])
                        if prvPort not in entry["ports"]:
                            entry["ports"].append(prvPort)

                entry["ports"].sort()
                entries.append(entry)
            entries.sort(key=lambda sortEntry: sortEntry["created"])
        except Exception as e:
            logger.error("Exception occurred in dockerInfoFetcher thread! - {}".format(e))
        sleep(5)


dockerFetchTask = Thread(target=fetchDockerInfo)
dockerFetchTask.daemon = True
dockerFetchTask.start()

logger.info("creating DNS Resolver...")


class DockerResolver(dnslib.server.BaseResolver):
    def resolve(self, dnsRequest, handler):
        reply = dnsRequest.reply()
        for q in dnsRequest.questions:
            try:
                if len(q.qname.label) >= 3:
                    if q.qname.label[-1].decode("UTF-8") == "local" and \
                            q.qname.label[-2].decode("UTF-8") == "vpn":
                        cmpstr = "/" + q.qname.label[-3].decode("UTF-8")
                        for e in entries:
                            try:
                                if e["name"] == cmpstr or cmpstr == "/*":
                                    for ip in e["ips"]:
                                        reply.add_answer(*RR.fromZone(str(e["name"][1:]) + ".vpn.local. 5 A " + ip))
                            except Exception as err2:
                                logger.error("Error processing docker entry {} - {}".format(e["name"],err2))
            except Exception as err:
                logger.error("Error processing questions in DNS request! - {}".format(err))
        return reply


DNSlogger = dnslib.server.DNSLogger(prefix=False)
dockerResolverObj = DockerResolver()
dnsPort = 8053
dnsServer = dnslib.server.DNSServer(resolver=dockerResolverObj, port=dnsPort, logger=DNSlogger)
dnsServer.start_thread()

logger.info("started DNS server on port {}".format(dnsPort))




@app.errorhandler(404)
def get404(error):
    logger.warning("404 -> {}".format(request.path))
    for i in entries:
        if i["name"] == request.path:
            return redirect("http://" + i["ips"][0] + ":" + i["ports"][0])
    return renderIndexFile()


@app.route("/")
def getIndexFile():
    return renderIndexFile()


@app.route("/api/getEntries")
def getEntries():
    eOut = []
    for e in entries:
        e["color"] = name2color(e["name"])
        eOut.append(e)
    return jsonify(eOut)


def renderIndexFile():
    return render_template('index.html')


def name2color(name):
    code = str(hashlib.md5(name.encode('utf-8')).hexdigest())
    return "rgba(" + str(int(code[0:2], 16)) + "," + str(int(code[2:4], 16)) + "," + str(int(code[4:6], 16)) + ",.5)"


@app.route("/api/name2color/<name>")
def name2colorRoute(name):
    return jsonify({name: name2color(name)})

