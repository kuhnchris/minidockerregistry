from threading import Thread
from time import sleep
from app.modules.common import logger, common
from app.modules.interfaces.services import CommonServiceInterface
from app.modules.containers.podman import PodmanContainers


class ContainerPodmanService(CommonServiceInterface):
    def __init__(self, timeBetweenUpdates=5) -> None:
        super().__init__()
        self.containerObject = PodmanContainers()
        self.threadObject = Thread(target=self.threadFunction)
        self.threadObject.daemon = True
        self.timeBetweenUpdates = timeBetweenUpdates

    def startThread(self):
        self.threadObject.start()

    def startService(self):
        self.fetchObjectsFromDocker()
        self.startThread()

    def fetchObjectsFromDocker(self):
        common.container_data.fromPodmanContainersAPI(self.containerObject.getContainers())
        # Common.groups = self.containerObject.getGroups()

    def threadFunction(self):
        logger.info("Starting podman fetching endless loop...")
        while True:
            logger.debug("New loop call - fetching docker info")
            self.fetchObjectsFromDocker()
            sleep(self.timeBetweenUpdates)
