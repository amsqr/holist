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
        favorite = Favorite()

        holist = Resource()
        holist.putChild("web", File("./web"))

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
    def __init__(self):
        self.favorites = []

    def render_GET(self, request):
        request.setHeader("content-type", "application/json")
        request.setHeader('Access-Control-Allow-Origin', '*')
        request.setHeader('Access-Control-Allow-Methods', 'GET')

        ln.info("Favorites: %s", self.favorites)
        return json.dumps(self.controller.retrieveDocuments(self.favorites))

    def render_POST(self, request):
        request.setHeader('Access-Control-Allow-Origin', '*')
        request.setHeader('Access-Control-Allow-Methods', 'GET')

        ids = [cgi.escape(docid) for docid in request.args["document_id"]]
        if not ids:
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
"""
        return json.dumps({
            "documents": [
                {
                    "id": "article1",
                    "date": "2014-06-13 18:08:42",
                    "title": "Holist IPO",
                    "text": "blah blah blah IPO"
                },
                {
                    "id": "article2",
                    "date": "2014-06-04 18:08:14",
                    "title": "Holist IPO successful",
                    "text": "blah blah blah IPO"
                },
                {
                    "id": "article3",
                    "date": "2014-06-01 18:00:00 ",
                    "title": "What does the Holist IPO mean for you?",
                    "text": "blah blah blah IPO"
                }
            ]
        })
"""

class CompleteSearch(Resource):
    def __init__(self, controller):
        self.controller = controller

    def render_GET(self, request):
        searchString = cgi.escape(request.args["entityName"][0])
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
"""
        return json.dumps({
            "documents":[
                {
                    "id": "article131",
                    "title": "Introducing Holist",
                    "text": "blah blah blah IPO"
                },
                {
                    "id": "article2123",
                    "title": "Palantir looking to acquire Holist",
                    "text": "blah blah blah IPO"
                },
                {
                    "id": "article3",
                    "title": "What does the Holist IPO mean for you?",
                    "text": "blah blah blah IPO"
                }
            ]
        })"""