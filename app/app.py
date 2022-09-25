from modules import common
from modules import flask
from modules import docker
from modules import dns
import os
import time

if __name__ == "__main__":
    docker.DockerInfoGatheringClass.startThread()
    if os.environ.get("ENABLE_DNS", "False").lower() != "false":
        dns.DockerDNSResolverClass.startThread()
    if os.environ.get("ENABLE_HTTP", "False").lower() != "false":
        flask.FlaskModule.startApp()
    else:
        while True:
            time.sleep(1)