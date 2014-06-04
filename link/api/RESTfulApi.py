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

        searchApi = SearchEntity(self.controller)
        notifyApi = Notify(self.controller)

        root.putChild("search_entity", searchApi)
        root.putChild("notify", notifyApi)

        factory = Site(root)
        reactor.listenTCP(config.link_node_port, factory)

class Notify(Resource):
    def __init__(self, controller):
        self.controller = controller
    def render_POST(self, request): # new data available
        ln.info("New data is available.")
        return json.dumps({"word":"sure bro"})

# this API returns a graph for a given entity string
class SearchEntity(Resource):
    def __init__(self, controller):
        self.controller = controller
    def render_GET(self, request):
        ln.info("Somebody just performed a search.")
        return json.dumps({"result":"We have to work on that."})

#
class RetrieveArticles(Resource):
    def __init__(self, controller):
        self.controller = controller
    def render_GET(self, request):
        ln.info("Somebody just performed a search.")
        return json.dumps({"result":"We have to work on that."})