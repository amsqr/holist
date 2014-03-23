from holist.util.util import *
ln = getModuleLogger(__name__)

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
        reactor.listenTCP(8082, factory)

class RegisterListener(Resource): 
    #todo: some checks for ip, port correctness
    def __init__(self, controller):
        self.controller = controller
    def render_POST(self, request):
        ip = cgi.escape(request.args["ip"][0])
        port = cgi.escape(request.args["port"][0])
        if None not in (ip, port):
            self.controller.registerListener(ip, port)
            return json.dumps({"success"}) 
        else:
            return json.dumps({"failure"}) 

class Notify(Resource): 
    def __init__(self, controller):
        self.controller = controller
    def render_POST(self, request): # new data available
        self.controller.onNewData()
        return json.dumps({"siiiick"}) 