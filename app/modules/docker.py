import logging
import docker
from threading import Thread
from time import sleep
from .common import Common
logger = logging.getLogger(__name__)

class DockerInfoGatheringClass():
    dockerClient = None
    dockerFetchTask = None
    
    def startThread():   
        DockerInfoGatheringClass.dockerFetchTask = Thread(target=DockerInfoGatheringClass.endlessLoop)
        DockerInfoGatheringClass.dockerFetchTask.daemon = True
        DockerInfoGatheringClass.dockerFetchTask.start()
    
    def getDockerClient():
        if DockerInfoGatheringClass.dockerClient == None:
            DockerInfoGatheringClass.dockerClient = docker.from_env()
        
        return DockerInfoGatheringClass.dockerClient
            
        
    def endlessLoop():
        logger.info("Starting docker fetching endless loop")
        while True:
            logger.debug("New loop call - fetching docker info")
            DockerInfoGatheringClass.fetchDockerInfo()
            sleep(5)

    def fetchDockerInfo():
        try:
            entries = []
            for c in DockerInfoGatheringClass.getDockerClient().containers():
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

            Common.entries.clear()
            Common.entries = Common.entries + entries
        except Exception as e:
            logger.error("Exception occurred in dockerInfoFetcher thread! - {}".format(e))


