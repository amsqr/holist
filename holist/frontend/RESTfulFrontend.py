from holist.util.util import *
ln = getModuleLogger(__name__)

from holist.util import config

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

        queryTextPage = QueryText(self.controller)
        queryIdPage = QueryId(self.controller)
        registerPage = RegisterListener(self.controller)
        notifyPage = Notify(self.controller)
        
        root.putChild("query_text", queryTextPage)
        root.putChild("query_id", queryIdPage)
        root.putChild("register_listener", registerPage)
        root.putChild("notify", notifyPage)

        factory = Site(root)
        reactor.listenTCP(config.holistcoreport, factory)

class QueryText(Resource):
    def __init__(self, controller):
        self.controller = controller

    def render_GET(self, request):
        #query = cgi.escape(request.args["query"][0])
        query = request.args["text"][0]
        queryResults = self.controller.queryText(query) # format is already {"LSA": [(1,0.9), (3,0.8),(2,0.1), ...],"Geo":[(1,0.9), (3,0.8),(2,0.1),...],... }
        return json.dumps(queryResults) # convert tuples, we're making sure it's valid json

class QueryId(Resource):
    def __init__(self, controller):
        self.controller = controller

    def render_GET(self, request):
        queryId = int(request.args["id"][0])
        queryResults = self.controller.queryId(queryId)
        return json.dumps(queryResults)

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
        self.controller.notifyNewDocuments()
        return json.dumps({"word":"sure bro"}) 