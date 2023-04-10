from app.modules.services.containers import ContainerService
from app.modules.services.dns import DNSServerService
from app.modules.services.webserver import WebServerService
import os
import time


def start():
    services = []
    if os.environ.get("ENABLE_CONTAINERS", "True").lower() != "false":
        services.append(ContainerService())
    if os.environ.get("ENABLE_DNS", "False").lower() != "false":
        services.append(DNSServerService())
    if os.environ.get("ENABLE_HTTP", "False").lower() != "false":
        services.append(WebServerService())
    else:
        while True:
            time.sleep(1)

    for service in services:
        service.startService()
