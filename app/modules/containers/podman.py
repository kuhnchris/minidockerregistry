from podman import podmanClient
from app.modules.interfaces.containers import CommonContainerInterface
from app import common


class PodmanContainers(CommonContainerInterface):
    def __init__(self):
        self.podmanClient = None
        common.logger.debug("Initializing logger")

    def _getClient(self):
        if self.podmanClient is None:
            self.podmanClient = podmanClient()

        return self.podmanClient
