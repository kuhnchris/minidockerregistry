from flask import Flask, jsonify, render_template, request, redirect
from app.modules.common import common, logger
from app.modules.interfaces.services import CommonServiceInterface
import hashlib
import os
import json


class WebServerService(CommonServiceInterface):
    def __init__(self) -> None:
        super().__init__()
        self.baseDir = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + "/../"
        self.httpPort = os.environ.get("HTTP_PORT", 8080)
        self.httpHost = os.environ.get("HTTP_HOST", "localhost")
        self.flaskDebug = False if os.environ.get("ENABLE_FLASK_DEBUG", "False").lower() == "false" else True

        self.staticFolderDir = self.baseDir + 'files/static/'
        self.scriptRoot = os.getenv('SCRIPT_NAME', '')
        self.staticUrlPath = '/static/'

        self.flaskTemplateFolder = self.baseDir + "files/"
        self.flaskStaticUrlPath = self.scriptRoot + '/' + self.staticUrlPath
        self.appFlaskObj = Flask(__name__,
                                 template_folder=self.flaskTemplateFolder,
                                 static_url_path=self.flaskStaticUrlPath,
                                 static_folder=self.staticFolderDir)
        self.appFlaskObj.register_error_handler(404, self.get404)
        self.appFlaskObj.add_url_rule("/", view_func=self.getIndexFile)
        self.appFlaskObj.add_url_rule("/api/raw/podman/containers", view_func=self.apiGetPodmanContainersRaw)
        self.appFlaskObj.add_url_rule("/api/raw/podman/groups", view_func=self.apiGetPodmanGroupsRaw)
        self.appFlaskObj.add_url_rule("/api/raw/podman/networks", view_func=self.apiGetPodmanNetworksRaw)
        self.appFlaskObj.add_url_rule("/api/getEntries", view_func=self.getEntries)
        self.appFlaskObj.add_url_rule("/api/getGroups", view_func=self.getGroups)
        self.appFlaskObj.add_url_rule("/api/getConfig", view_func=self.getConfig)
        self.appFlaskObj.add_url_rule("/api/name2color/<name>", view_func=self.name2colorRoute)

        if self.scriptRoot != '':
            logger.info("mounting application over at: " + self.scriptRoot)
            from werkzeug.middleware.dispatcher import DispatcherMiddleware
            self.appFlaskObj.wsgi_app = DispatcherMiddleware(self.appFlaskObj.wsgi_app, {self.scriptRoot: self.appFlaskObj})

    def startService(self):
        logger.info("Starting flask web server on {} port {} - http://{}:{}/".format(self.httpHost, self.httpPort, self.httpHost, self.httpPort))
        logger.info("Serving static files from: {} loading at: {}".format(self.staticUrlPath, self.staticFolderDir))
        try:
            self.appFlaskObj.run(host=self.httpHost, port=self.httpPort, debug=self.flaskDebug)
        except SystemExit as s:
            logger.warn("reloading... - " + str(s))
        except Exception as e:
            logger.warn("Exception occured during run: " + str(e))
  
    def startThread(self):
        return super().startThread()
    
    def stopThread(self):
        return super().stopThread()
    
    def get404(self, error):
        logger.warning("404 -> {}; {}".format(request.path, str(error)))
        for e in common.container_data.containers:
            if e.name == request.path:
                return redirect("http://" + e.networks[0] + ":" + e.ports[0])
        return self.renderIndexFile()

    def getIndexFile(self):
        return self.renderIndexFile()

    def getEntries(self):
        eOut = []
        logger.debug("Entries: {}".format(common.container_data.containers))
        for e in common.container_data.containers:
            e.ui_color = self.name2color(e.name)
            eOut.append(json.loads(e.json()))
        return eOut

    def apiGetPodmanContainersRaw(self):
        from app.modules.services.containersPodman import ContainerPodmanService
        return ContainerPodmanService().containerObject.getContainers()
        
    def apiGetPodmanGroupsRaw(self):
        from app.modules.services.containersPodman import ContainerPodmanService
        return ContainerPodmanService().containerObject.getGroups()
    
    def apiGetPodmanNetworksRaw(self):
        from app.modules.services.containersPodman import ContainerPodmanService
        return ContainerPodmanService().containerObject.getNetworks()

    def getConfig(self):
        return jsonify(common.features)
    
    def getGroups(self):
        return jsonify(common.container_data.groups)

    def name2colorRoute(self, name):
        return jsonify({name: self.name2color(name)})

    def renderIndexFile(self):
        return render_template('index.html')

    def name2color(self, name):
        code = str(hashlib.md5(name.encode('utf-8')).hexdigest())
        return "rgba(" + str(int(code[0:2], 16)) + "," + str(int(code[2:4], 16)) + "," + str(int(code[4:6], 16)) + ",.5)"
