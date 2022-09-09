import hashlib
import logging
import docker
from threading import Thread
from time import sleep
from flask import Flask, jsonify, render_template, request, redirect

logger = logging.getLogger(__name__)
app = Flask(__name__, template_folder=".",
            static_url_path='/static/',
            static_folder='static/')

entries = []


def fetchDockerInfo():
    while True:
        logger.info("fetching Docker info...")
        client = docker.from_env()
        for c in client.containers():
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
        sleep(5)


dockerFetchTask = Thread(target=fetchDockerInfo)
dockerFetchTask.daemon = True
dockerFetchTask.run()


def name2color(name):
    code = str(hashlib.md5(name.encode('utf-8')).hexdigest())
    return "rgba(" + str(int(code[0:2], 16)) + "," + str(int(code[2:4], 16)) + "," + str(int(code[4:6], 16)) + ",.5)"


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
    return jsonify(entries)

def renderIndexFile():
    return render_template('index.html')
