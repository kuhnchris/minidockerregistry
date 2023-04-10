from podman import PodmanClient
from app.modules.interfaces.containers import CommonContainerInterface
from app.modules.common import logger
import os


class PodmanContainers(CommonContainerInterface):
    def __init__(self):
        self.podmanClient: PodmanClient = None
        self.podmanBaseUrl = os.environ.get("DOCKER_HOST", "")

        logger.debug("Initializing logger for Podman Containers...")

    def _getClient(self) -> PodmanClient:
        if self.podmanClient is None:
            self.podmanClient = PodmanClient(base_url=self.podmanBaseUrl)

        return self.podmanClient
    
    def getContainers(self):
        entries = []
        for c in self._getClient().containers.list(all=True):
            entries.append(c.attrs)
        return entries

    def getGroups(self):
        entries = []
        for p in self._getClient().pods.list():
            entries.append(p.attrs)
        return entries

    def getNetworks(self):
        return [p.attrs for p in self._getClient().networks.list()]
