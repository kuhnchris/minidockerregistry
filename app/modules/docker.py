from app.modules.common import logger, Common
from threading import Thread
from time import sleep
from app.modules.containers.docker import DockerContainers


class DockerInfoGatheringClass():
    def __init__(self) -> None:
        self.dockerFetchTask = None
        self.containerObject = DockerContainers()

    def startThread(self):
        self.dockerFetchTask = Thread(target=self.endlessLoop)
        self.dockerFetchTask.daemon = True
        self.dockerFetchTask.start()
    
    def fetchDockerInfo(self):
        Common.entries = self.containerObject.getContainers()

    def endlessLoop(self):
        logger.info("Starting docker fetching endless loop")
        while True:
            logger.debug("New loop call - fetching docker info")
            self.fetchDockerInfo()
            sleep(5)
