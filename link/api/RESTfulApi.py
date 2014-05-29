__author__ = 'raoulfriedrich'

from core.util.util import *
ln = getModuleLogger(__name__)

from twisted.web.resource import Resource
from twisted.web.server import Site
import json

class RESTfulApi(object):

    def __init__(self, controller):
        self.controller = controller
        self.setupResources()

    def setupResources(self):
        root = Resource()

        searchApi = PerformSearch(self.controller)
        notifyApi = Notify(self.controller)

        root.putChild("perform_search", searchApi)
        root.putChild("notify", notifyApi)

        factory = Site(root)
        reactor.listenTCP(config.link_node_port, factory)

class Notify(Resource):
    def __init__(self, controller):
        self.controller = controller
    def render_POST(self, request): # new data available
        ln.info("New data is available.")
        return json.dumps({"word":"sure bro"})

class PerformSearch(Resource):
    def __init__(self, controller):
        self.controller = controller
    def render_POST(self, request):
        ln.info("Somebody just performed a search.")
        return json.dumps({"result":"We have to work on that."})