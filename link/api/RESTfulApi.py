__author__ = 'raoulfriedrich'

from core.util.util import *
ln = getModuleLogger(__name__)

from twisted.web.resource import Resource

from twisted.web.server import Site
from twisted.web.static import File
from twisted.internet import reactor
import json
import cgi


class RESTfulApi(object):

    def __init__(self, controller):
        self.controller = controller
        self.setupResources()

    def setupResources(self):
        root = Resource()

        complete = CompleteSearch(self.controller)
        searchApi = SearchEntity(self.controller)
        retrieveApi = RetrieveDocuments(self.controller)
        searchSimilarApi = SearchSimilarDocuments(self.controller)
        favorite = Favorite(self.controller)

        holist = Holist()
        holist.putChild("web", File("./holist-web"))

        root.putChild("holist", holist)
        root.putChild("favorites", favorite)
        root.putChild("complete_search", complete)
        root.putChild("search_entity", searchApi)
        root.putChild("retrieve_documents", retrieveApi)
        root.putChild("search_similar", searchSimilarApi)


        factory = Site(root)
        reactor.listenTCP(config.link_node_port, factory)

        commandRoot = Resource()
        command = LinkControlInterface(self.controller)
        commandRoot.putChild("command", command)
        commandFactory = Site(commandRoot)
        reactor.listenTCP(config.link_node_control_port, commandFactory)


class Holist(Resource):
    def getChild(self, path, request):
        ln.debug("incoming request for path %s", path)
        return Resource.getChild(self, path, request)

class LinkControlInterface(Resource):
    def __init__(self, controller):
        self.controller = controller

    def render_GET(self, request):
        command = cgi.escape(request.args["command"][0])
        if command == "rebuild":
            reactor.callLater(5, self.controller.rebuildIndex)
            request.setResponseCode(200)
            return "Triggered index rebuild."

        request.setResponseCode(400)
        return "Unknown command."


class Favorite(Resource):
    def __init__(self, controller):
        self.favorites = []
        self.controller = controller

    def render_GET(self, request):
        request.setHeader("content-type", "application/json")
        request.setHeader('Access-Control-Allow-Origin', '*')
        request.setHeader('Access-Control-Allow-Methods', 'GET')

        ln.info("Favorites: %s", self.favorites)
        return json.dumps(self.controller.retrieveDocuments(self.favorites))

    def render_POST(self, request):
        request.setHeader("content-type", "application/json")
        request.setHeader('Access-Control-Allow-Origin', '*')
        request.setHeader('Access-Control-Allow-Methods', 'POST')
        try:
            ids = [cgi.escape(docid) for docid in request.args["document_id"]]
        except KeyError:
            request.setResponseCode(400)
            return "No document_id found."

        self.favorites += ids

        return "Ok."


# this API returns a graph for a given entity string
class SearchEntity(Resource):
    def __init__(self, controller):
        self.controller = controller

    def render_GET(self, request):
        request.setHeader("content-type", "application/json")
        request.setHeader('Access-Control-Allow-Origin', '*')
        request.setHeader('Access-Control-Allow-Methods', 'GET')
        try:
            entityName = cgi.escape(request.args["entityName"][0])
        except KeyError:
            request.setResponseCode(400)
            return json.dumps({"reason": "need entityName parameter"})

        ln.info("Somebody just performed a search with entityName = %s.", entityName)
        return json.dumps(self.controller.performEntitySearch(entityName), indent=2)


class RetrieveDocuments(Resource):
    def __init__(self, controller):
        self.controller = controller

    def render_GET(self, request):
        request.setHeader("content-type", "application/json")
        request.setHeader('Access-Control-Allow-Origin', '*')
        request.setHeader('Access-Control-Allow-Methods', 'GET')
        documentIds = [cgi.escape(d) for d in request.args["document"]]

        ln.info("Somebody is trying to retrieve documents: %s", documentIds)
        # TODO: create LinkController.retrieveDocuments(documentIds)
        return json.dumps(self.controller.retrieveDocuments(documentIds))


class CompleteSearch(Resource):
    def __init__(self, controller):
        self.controller = controller

    def render_GET(self, request):
        request.setHeader('Access-Control-Allow-Origin', '*')
        request.setHeader('Access-Control-Allow-Methods', 'GET')
        try:
            searchString = cgi.escape(request.args["entityName"][0])
        except KeyError:
            request.setResponseCode(400)
            return "no entity name requested"
        return json.dumps(self.controller.completeSearch(searchString))


class SearchSimilarDocuments(Resource):
    def __init__(self, controller):
        self.controller = controller

    def render_GET(self, request):
        request.setHeader("content-type", "application/json")
        request.setHeader('Access-Control-Allow-Origin', '*')
        request.setHeader('Access-Control-Allow-Methods', 'GET')

        docId = cgi.escape(request.args["id"][0])

        ln.info("Somebody just performed a search for similar documents: %s.", docId)
        # TODO: create LinkController.searchSimilar
        return json.dumps(self.controller.searchSimilar(docId))