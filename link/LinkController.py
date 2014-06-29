__author__ = 'raoulfriedrich'

from core.util.util import *
import logging
logging.basicConfig(format=config.logFormat, level=logging.DEBUG if config.showDebugLogs else logging.INFO)
ln = getModuleLogger(__name__)

from twisted.internet import reactor
from core.model.server.NodeCommunicator import NodeCommunicator
from link.api.RESTfulApi import RESTfulApi
from link.NamedEntityIndex import NamedEntityIndex
from link.ClusterStratgy import SimpleClusterStrategy
from link.ClusterStratgy import DBSCANClusterStrategy
from collections import defaultdict


CORE_IP = "localhost"
REGISTER_PORT = config.holistcoreport
LISTEN_PORT = config.link_node_port + 1
TESTING = True
REBUILD = False

class Document:
    pass


def bsonToClientBson(bson):
    clientDoc = {}
    clientDoc["id"] = str(bson["_id"])
    clientDoc["lsa"] = bson["vectors"]["LSA"]
    clientDoc["title"] = bson["title"]
    clientDoc["description"] = bson["description"]
    clientDoc["text"] = bson["text"]
    clientDoc["link"] = bson["link"]
    clientDoc["timestamp"] = bson["timestamp"]
    return clientDoc

from link.LshManager import LshManager

class LinkController(object):

    def __init__(self):
        # init and start node communicator (connection to core node)
        self.nodeCommunicator = NodeCommunicator(self, LISTEN_PORT, strategy=False)
        self.nodeCommunicator.registerWithNode(CORE_IP, REGISTER_PORT)

        # init lsh index manager, indexes all documents for searching
        self.lshManager = LshManager()


        self.namedEntityIndex = NamedEntityIndex()

        # init clustering strategy to cluster search results (combine them into nodes)
        self.clusterStrategy = DBSCANClusterStrategy(self.namedEntityIndex, self.lshManager)
        #self.clusterStrategy = SimpleClusterStrategy(self.namedEntityIndex, self.lshManager)

        # init rest apis
        self.frontend = RESTfulApi(self)

        # if rebuild flag is true, rebuild the whole lsh index
        if REBUILD:
            self.rebuildIndex()

        # start server
        ln.info("running reactor.")
        reactor.run()

    def rebuildIndex(self):
        ln.info("Triggered complete index rebuild.")
        lshcount, nercount, lshfailed, nerfailed = 0, 0, 0, 0

        self.lshManager.clearIndex()
        self.namedEntityIndex.index = defaultdict(list)

        client = getDatabaseConnection()
        for articleBSON in client.holist.articles.find():
            doc = convertToDocument(articleBSON)
            try:
                self.lshManager.addDocument(doc)
                lshcount += 1
            except KeyError:
                #ln.debug("Document doesn't have LSA vector: %s", articleBSON["_id"])
                lshfailed += 1
            try:
                self.namedEntityIndex.addDocument(doc)
                nercount += 1
            except KeyError:
                #ln.debug("Document doesn't have NER annotations: %s", articleBSON["_id"])
                nerfailed += 1
        ln.info("Rebuild complete. Added %s LSH and %s NER documents, failed on %s LSA and %s NER.",
                lshcount, nercount, lshfailed, nerfailed)
        self.namedEntityIndex.save()

    def handleNewDocuments(self, newDocuments):
        documents = []
        for docDict in newDocuments:
            document = Document()
            document.__dict__ = docDict
            documents.append(document)
        ln.debug("Got %s new documents.", len(documents))

        for document in documents:
            self.lshManager.addDocument(document)
            self.namedEntityIndex.addDocument(document)
        # TODO: better load/save of namedEntityIndex
        self.namedEntityIndex.save()

    def completeSearch(self, searchString):
        return sorted([namedEntity for namedEntity in self.namedEntityIndex.index
                      if namedEntity.startswith(searchString)],
                      key=lambda s: len(s))

    def performEntitySearch(self, entityName):
        # check that we know this entity
        if not self.namedEntityIndex.query(entityName) and not TESTING:
            return {"result": "False", "reason": "Unknown entity."}

        nodes, adj,  success = self.clusterStrategy.cluster(entityName)

        if not success:
            return nodes, adj

        return {"nodes": nodes, "links": adj}

    def retrieveDocuments(self, documentIds):
        client = getDatabaseConnection()
        results = []
        for docId in documentIds:
            try:
                bson = client.holist.articles.find({"_id": docId}).next()
                clientDoc = bsonToClientBson(bson)
                results.append(clientDoc)
            except StopIteration:
                ln.error("Client requested ID not in database: %s", docId)
        return {"documents": results}

    def searchSimilar(self, docId):
        client = getDatabaseConnection()
        try:
            bson = client.holist.articles.find({"_id": docId}).next()

        except StopIteration:
            ln.error("Client requested ID not in database: %s", docId)
            return []
        document = convertToDocument(bson)
        similar = self.lshManager.getSimilarDocuments(document)
        res = []
        for doc in similar:
            res.append(doc)
        return {"documents": res}
