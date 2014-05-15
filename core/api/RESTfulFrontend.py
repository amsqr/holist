from core.util.util import *
ln = getModuleLogger(__name__)

from core.util import config

from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.internet import reactor
import cgi
import json

class RESTfulFrontend(object):

    def __init__(self, controller):
        self.controller = controller
        self.setupResources()

    def setupResources(self):
        root = Resource()

        registerPage = RegisterListener(self.controller)
        notifyPage = Notify(self.controller)
        
        root.putChild("register_listener", registerPage)
        root.putChild("notify", notifyPage)

        factory = Site(root)
        reactor.listenTCP(config.holistcoreport, factory)


class RegisterListener(Resource): 
    #todo: some checks for ip, port correctness
    def __init__(self, controller):
        self.controller = controller
    def render_POST(self, request):
        ln.debug("received registration request: %s", request.args)
        ip = cgi.escape(request.args["ip"][0])
        port = cgi.escape(request.args["port"][0])
        if None not in (ip, port):
            self.controller.registerListener(ip, port)
            return json.dumps({"result":"success"}) 
        else:
            return json.dumps({"result":"failure"}) 

class Notify(Resource): 
    def __init__(self, controller):
        self.controller = controller
    def render_POST(self, request): # new data available
        self.controller.onNewDocuments()
        return json.dumps({"word":"sure bro"}) 