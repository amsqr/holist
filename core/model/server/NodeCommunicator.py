from core.util.util import *
ln = getModuleLogger(__name__)

from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.internet import reactor
from twisted.internet.threads import deferToThread
from shared.Heartbeat.TwistedBeatServer import TwistedBeatServer
from twisted.internet.task import LoopingCall

import requests
import json
import time
import cgi

class Task(Resource):
    def __init__(self, controller, strategy):
        self.controller = controller
        self.isStrategy = strategy

    def render_POST(self, request):
        data = request.content.read()
        ln.debug("received task: %s", data[:1000])
        try:
            data = json.loads(data)
        except:
            ln.error("got invalid data: %s", data[:1000])
            return 0

        if self.isStrategy:
            sender = data["respondTo"]
            docs = data["documents"]
            self.controller.queueDocuments(sender, docs)
        else:
            docs = data["documents"]
            self.controller.handleNewDocuments(docs)
        ln.info("Queued task.")

        return json.dumps({"result": "ok"})

class SmallTask(Resource):
    def __init__(self, controller):
        self.controller = controller

    def render_GET(self, request):
        document = cgi.escape(request.args["document"][0])
        return json.dumps(self.controller.handleOne(document))

class NodeCommunicator(object):

    def __init__(self, controller, listenPort, strategy=True):
        self.controller = controller
        self.listenPort = listenPort
        self.isStrategy = strategy

        self.setupResources()
        self.loopingCall = None

    def setupResources(self):
        root = Resource()
        taskPage = Task(self.controller, self.isStrategy)
        if self.isStrategy:
            root.putChild("small_task", SmallTask(self.controller))
            root.putChild("task", taskPage)
        else:
            root.putChild("notify", taskPage)
        factory = Site(root)
        reactor.listenTCP(self.listenPort, factory)

        ln.debug("Listening on port %s", self.listenPort)

    def respond(self, sender, data):
        ln.debug("attempting to respond to %s", sender)
        requests.post(sender, data=json.dumps(data))

    def registerWithNode(self, nodeIp, registerPort, maxRetries=30):
        deferToThread(self._registerWithNode, nodeIp, registerPort, maxRetries)

    def _registerWithNode(self, nodeIp, registerPort, maxRetries):
        for x in range(maxRetries):
            ln.debug("attempting to register with core on %s:%s", nodeIp, registerPort)
            try:
                if self.isStrategy:
                    r = requests.post("http://" + nodeIp + ":"+str(registerPort)+"/register_strategy",
                                      {"strategy": self.controller.NAME, "ip": "localhost", "port": self.listenPort})
                else:
                    r = requests.post("http://" + nodeIp + ":"+str(registerPort)+"/register_listener",
                                      {"ip": "localhost", "port": self.listenPort})

            except Exception as e:
                ln.error("Couldn't connect to core on localhost:%s", registerPort)
                time.sleep(2)
                continue
            if r.status_code == 200:
                ln.info("registered with core.")
                self.heartbeatServer = TwistedBeatServer(self.handleServerDown, self.listenPort)
                return True
        return False

    def handleServerDown(self, clients):pass
