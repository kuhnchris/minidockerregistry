import docker
import hashlib
from flask import Flask
from flask import render_template
from flask import request, redirect

app = Flask(__name__, template_folder=".")

def name2color(name):
  code = str(hashlib.md5(name.encode('utf-8')).hexdigest())
  return "rgba("+str(int(code[0:2],16))+","+str(int(code[2:4],16))+","+str(int(code[4:6],16))+",.5)"
  #return code

@app.errorhandler(404)
def get404(error):
    print(request.path)
    entries = getDockerEntries()
    for i in entries:
        if i["name"] == request.path:
            return redirect("http://"+i["ips"][0]+":"+i["ports"][0])
    return renderResponse()

@app.route("/")
def getAll():
    return renderResponse()

def getDockerEntries():
    entries = []
    client = docker.from_env()
    for c in client.containers():
        entry = { "name":"", "ips":[], "ports": []}
        entry["name"] = ", ".join(c["Names"])
        nwrks = c["NetworkSettings"]["Networks"]
        for k in nwrks.keys():
            ip=nwrks[k]["IPAddress"]
            entry["ips"].append(ip)

        for p in c["Ports"]:
            if p["Type"] == "tcp":
                entry["ports"].append(str(p["PrivatePort"]))
    #    print()
    #    print(c["Ports"])
        entries.append(entry)
    return entries

def renderResponse():
    entries = getDockerEntries()
    return render_template('template.j2',entries=entries, n2c=name2color, request=request)
