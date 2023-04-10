from threading import Thread
from time import sleep
from app.modules.common import logger, common
from app.modules.interfaces.services import CommonServiceInterface
from app.modules.containers.docker import DockerContainers


class ContainerDockerService(CommonServiceInterface):
    def __init__(self, timeBetweenUpdates=5) -> None:
        super().__init__()
        self.containerObject = DockerContainers()
        self.threadObject = Thread(target=self.threadFunction)
        self.threadObject.daemon = True
        self.timeBetweenUpdates = timeBetweenUpdates

    def startThread(self):
        self.threadObject.start()

    def startService(self):
        self.fetchObjectsFromDocker()
        self.startThread()

    def fetchObjectsFromDocker(self):
        common.container_data.fromDockerContainersAPI(self.containerObject.getContainers())

    def threadFunction(self):
        logger.info("Starting docker fetching endless loop...")
        while True:
            logger.debug("New loop call - fetching docker info")
            self.fetchObjectsFromDocker()
            sleep(self.timeBetweenUpdates)
