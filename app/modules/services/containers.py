from app.modules.interfaces.services import CommonServiceInterface
from app.modules.containers.docker import DockerContainers
from app.modules.services.containersDocker import ContainerDockerService
from app.modules.services.containersPodman import ContainerPodmanService


class ContainerService(CommonServiceInterface):
    def __init__(self) -> None:
        super().__init__()
        self.containerAPIObject = DockerContainers()
        self.innerService = None
        if self.checkEndpointIsPodman():
            self.isPodman = True
            self.innerService = ContainerPodmanService()
        else:
            self.innerService = ContainerDockerService()

    def checkEndpointIsPodman(self) -> None:
        try:
            return True in [cc["Name"] == "Podman Engine" for cc in self.containerAPIObject._getClient().version()["Components"]]
        except Exception:
            return False
   
    def startService(self):
        self.innerService.startService()

    def startThread(self):
        self.innerService.startThread()
    
    def stopThread(self):
        self.innerService.stopThread()
