import typing
from typing import Optional
from pydantic.main import BaseModel


class CommonContainerInterface():
    def getContainers(self) -> typing.List:
        return []

    def getGroups(self):
        return []

    def __getClient():
        raise NotImplementedError


class CommonContainerDataStructureNetwork(BaseModel):
    name: str
    ip: Optional[str]


class CommonContainerDataStructureNetworkPort(BaseModel):
    source_port: int
    target_port: int
    target_ip: str
    protocol: str


class CommonContainerDataStructureContainerInfo(BaseModel):
    name: str
    id: str
    networks: Optional[list[CommonContainerDataStructureNetwork]] = []
    ports: Optional[list[CommonContainerDataStructureNetworkPort]] = []
    parent: Optional[BaseModel]
    state: Optional[str]

    ui_color: Optional[str]


class CommonContainerDataStructureGroups(BaseModel):
    name: str
    id: Optional[str]
    containers: Optional[list[CommonContainerDataStructureContainerInfo]] = []


class CommonContainerDataStructure(BaseModel):
    containers: Optional[list[CommonContainerDataStructureContainerInfo]] = []
    groups: Optional[list[CommonContainerDataStructureGroups]] = []

    def fromPodmanContainersAPI(self, jsonData):
        self.containers.clear()
        self.groups.clear()
        for entry in jsonData:
            c = CommonContainerDataStructureContainerInfo(name=entry["Names"][0],
                                                          id=entry["Id"],
                                                          state=entry["State"])
            if "Networks" in entry and entry["Networks"] is not None:
                for n in entry["Networks"]:
                    c.networks.append(CommonContainerDataStructureNetwork(name=n))
            if "Ports" in entry and entry["Ports"] is not None:
                for p in entry["Ports"]:
                    c.ports.append(CommonContainerDataStructureNetworkPort(source_port=p["container_port"],
                                                                           target_port=p["host_port"],
                                                                           target_ip=p["host_ip"],
                                                                           protocol=p["protocol"]))
            self.containers.append(c)
            
            if "Pod" in entry:
                if True not in [cc.id == entry["Pod"] for cc in self.groups]:
                    self.groups.append(CommonContainerDataStructureGroups(name=entry["PodName"], id=entry["Pod"]))
                
                for cc in self.groups:
                    if cc.id == entry["Pod"]:
                        cc.containers.append(c)

    def fromDockerContainersAPI(self, jsonData):
        pass
