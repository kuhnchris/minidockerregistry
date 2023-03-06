from app.modules.interfaces.containers import CommonContainerInterface
from app.modules.common import logger
import docker


class DockerContainers(CommonContainerInterface):
    def __init__(self):
        self.dockerClient = None

    def _getClient(self):
        if self.dockerClient is None:
            self.dockerClient = docker.from_env()

        return self.dockerClient

    def getContainers(self):
        return self.fetchDockerInfo()

    def fetchDockerInfo(self):
        try:
            entries = []
            for c in self._getClient().containers():
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
            return entries
        except Exception as e:
            logger.error("Exception occurred in fetchDockerInfo! - {}".format(e))
            return []
