__author__ = 'raoulfriedrich'

from core.util.util import *
ln = getModuleLogger(__name__)

from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.internet import reactor
import json
import cgi


class RESTfulApi(object):

    def __init__(self, controller):
        self.controller = controller
        self.setupResources()

    def setupResources(self):
        root = Resource()

        notifyApi = Notify(self.controller)
        searchApi = SearchEntity(self.controller)
        retrieveApi = RetrieveDocuments(self.controller)
        searchSimilarApi = SearchSimilarDocuments(self.controller)

        root.putChild("notify", notifyApi)
        root.putChild("search_entity", searchApi)
        root.putChild("retrieve_documents", retrieveApi)
        root.putChild("search_similar", searchSimilarApi)


        factory = Site(root)
        reactor.listenTCP(config.link_node_port, factory)


class Notify(Resource):
    def __init__(self, controller):
        self.controller = controller

    def render_POST(self, request): # new data available
        data = request.content.read()
        ln.debug("received task: %s", data[:1000])
        try:
            data = json.loads(data)
        except:
            ln.error("got invalid data: %s", data[:1000])
            return 0

        annotated = data["annotated_documents"]

        self.controller.handleNewDocuments(annotated)

        ln.info("New data is available.")
        return json.dumps({"word": "sure bro"})


# this API returns a graph for a given entity string
class SearchEntity(Resource):
    def __init__(self, controller):
        self.controller = controller

    def render_GET(self, request):
        entityName = cgi.escape(request.args["entityName"][0])

        ln.info("Somebody just performed a search with entityName = %s.", entityName)
        # TODO LinkController.performEntitySearch(entityName)
        self.controller.performEntitySearch(entityName)

        return json.dumps(
            {"nodes": [
                {
                    "id": "entity_id1234",
                    "title": "Holist"
                },
                {
                    "id": "cluster_1",
                    "title": "Holist IPO",
                    "documents": ["article1", "article2", "article3"]
                },
                {
                    "id": "cluster_2",
                    "title": "Holist joins y-combinator",
                    "documents": ["article3", "article6", "article10", "article4w32", "article12345"]
                },
                {
                    "id": "cluster_3",
                    "title": "Holist gets 3 billion valuation",
                    "documents": ["article1232", "article1115"]
                }
            ], "adj": [
                ("entity_id1234", "cluster_1"),
                ("entity_id1234", "cluster_2"),
                ("entity_id1234", "cluster_3")
            ]
            }
        )


class RetrieveDocuments(Resource):
    def __init__(self, controller):
        self.controller = controller

    def render_GET(self, request):
        documentIds = cgi.escape(request.args["document"])

        ln.info("Somebody is trying to retrieve documents: %s", documentIds)
        # TODO: create LinkController.retrieveDocuments(documentIds)
        self.controller.retrieveDocuments(documentIds)

        return json.dumps({
            "documents": [
                {
                    "id": "article1",
                    "title": "Holist IPO",
                    "text": "blah blah blah IPO"
                },
                {
                    "id": "article2",
                    "title": "Holist IPO successful",
                    "text": "blah blah blah IPO"
                },
                {
                    "id": "article3",
                    "title": "What does the Holist IPO mean for you?",
                    "text": "blah blah blah IPO"
                }
            ]
        })


class SearchSimilarDocuments(Resource):
    def __init__(self, controller):
        self.controller = controller

    def render_GET(self, request):
        docId = cgi.escape(request.args["document"][0])

        ln.info("Somebody just performed a search for similar documents: %s.", docId)
        # TODO: create LinkController.searchSimilar
        self.controller.searchSimilar(docId)

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
        })