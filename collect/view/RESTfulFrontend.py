from holist.util.util import *
ln = getModuleLogger(__name__)

from holist.util.util import config as holistConfig

from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.internet import reactor
import json

class RESTfulFrontend(object):
    def __init__(self, controller):
        self.controller = controller

        root = Resource()
        registerPage = RegisterListener(self.controller)
        root.putChild("status", StatusPage(self.controller))

        factory = Site(root)
        reactor.listenTCP(holistConfig.collectNodePort, factory)

class StatusPage(Resource):
    def __init__(self, controller):
        self.controller = controller
    def render_GET(self,request):
        return json.dumps(
            {"started":self.controller.started,
             "documentsOnStartup":self.controller.articlesOnStartup,
             "listeners":len(self.controller.listeners)
             "sources":[source.__class__]})

