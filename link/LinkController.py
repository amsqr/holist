__author__ = 'raoulfriedrich'

from core.util.util import *

import logging

logging.basicConfig(format=config.logFormat, level=logging.DEBUG if config.showDebugLogs else logging.INFO)
ln = getModuleLogger(__name__)

from twisted.internet import reactor


from link.api.RESTfulApi import RESTfulApi
from core.model.server.NodeCommunicator import NodeCommunicator
from link.LshManager import LshManager
from link.NamedEntityIndex import NamedEntityIndex
from link.ClusterStratgy import SimpleClusterStrategy

CORE_IP = "localhost"
REGISTER_PORT = config.holistcoreport
LISTEN_PORT = config.link_node_port + 1


class Document:
    pass

def bsonToClientBson(bson):
    clientDoc = {}
    clientDoc["id"] = str(bson["_id"])
    clientDoc["title"] = bson["title"]
    clientDoc["text"] = bson["text"]
    #TODO all documents MUST have timestamps
    clientDoc["timestamp"] = bson.get("timestamp", str(datetime.datetime.now()))
    return clientDoc

TESTING = True
REBUILD = False

class LinkController(object):

    def __init__(self):
        self.nodeCommunicator = NodeCommunicator(self, LISTEN_PORT, strategy=False)
        self.nodeCommunicator.registerWithNode(CORE_IP, REGISTER_PORT)

        self.lshManager = LshManager()
        self.namedEntityIndex = NamedEntityIndex()

        self.clusterStrategy = SimpleClusterStrategy(self.namedEntityIndex, self.lshManager)

        self.frontend = RESTfulApi(self)

        if REBUILD:
            self.rebuildIndex()

        # PUT THIS LINES WHEN CONNECTION TO CORE IS ESTABLISHED
        #heartbeatThread = HearbeatClient(CORE_IP, 43278)
        #heartbeatThread.start()

        ln.info("running reactor.")
        reactor.run()

    def rebuildIndex(self):
        ln.info("Triggered complete index rebuild.")
        count, failed = 0, 0
        self.lshManager.clearIndex()
        client = getDatabaseConnection()
        for articleBSON in client.holist.articles.find():
            doc = convertToDocument(articleBSON)
            try:
                self.lshManager.addDocument(doc)
                count += 1
            except KeyError as e:
                ln.exception(e)
                ln.debug("Document got keyerror: %s", articleBSON)
                failed += 1
        ln.info("Rebuild complete. Added %s documents, failed on %s.", count, failed)

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
