from flask import Flask, jsonify, render_template, request, redirect
from .common import Common
import hashlib
import logging
import os
logger = logging.getLogger(__name__)


class FlaskModule:        
    def startApp():
        baseDir = os.path.dirname(os.path.realpath(__file__)) + "/../"
        httpPort = os.environ.get("HTTP_PORT", 8080)
        httpHost = os.environ.get("HTTP_HOST","localhost")
        flaskDebug = False if os.environ.get("ENABLE_FLASK_DEBUG","False").lower() == "false" else True
        
        logger.info("Starting flask web server on {} port {} - http://{}:{}/".format(httpHost, httpPort, httpHost, httpPort))
        app = Flask(__name__, 
                    template_folder=baseDir + "files/",
                    static_url_path='/static/',
                    static_folder=baseDir + '/files/static/')
        app.register_error_handler(404, FlaskModule.get404)
        app.add_url_rule("/", view_func=FlaskModule.getIndexFile)
        app.add_url_rule("/api/getEntries", view_func=FlaskModule.getEntries)
        app.add_url_rule("/api/name2color/<name>", view_func=FlaskModule.name2colorRoute)
        app.run(host=httpHost, port=httpPort, debug=flaskDebug)

    def get404(error):
        logger.warning("404 -> {}".format(request.path))
        for i in Common.entries:
            if i["name"] == request.path:
                return redirect("http://" + i["ips"][0] + ":" + i["ports"][0])
        return FlaskModule.renderIndexFile()

    def getIndexFile():
        return FlaskModule.renderIndexFile()

    def getEntries():
        eOut = []
        logger.debug("Entries: {}".format(Common.entries))
        for e in Common.entries:
            e["color"] = FlaskModule.name2color(e["name"])
            eOut.append(e)
        return jsonify(eOut)

    def name2colorRoute(name):
        return jsonify({name: FlaskModule.name2color(name)})


    def renderIndexFile():
        return render_template('index.html')

    def name2color(name):
        code = str(hashlib.md5(name.encode('utf-8')).hexdigest())
        return "rgba(" + str(int(code[0:2], 16)) + "," + str(int(code[2:4], 16)) + "," + str(int(code[4:6], 16)) + ",.5)"

