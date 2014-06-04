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
LISTEN_PORT = config.link_node_port


class Document:
    pass


class LinkController(object):

    def __init__(self):
        self.nodeCommunicator = NodeCommunicator(self, LISTEN_PORT, strategy=False)
        self.nodeCommunicator.registerWithNode(CORE_IP, REGISTER_PORT)

        self.lshManager = LshManager()
        self.namedEntityIndex = NamedEntityIndex()

        self.clusterStrategy = SimpleClusterStrategy()

        self.frontend = RESTfulApi(self)

        ln.info("running reactor.")
        reactor.run()

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
        if not self.namedEntityIndex.query(entityName):
            return {"result": "False", "reason": "Unknown entity."}

        res, success = self.clusterStrategy.cluster(entityName)

        if not success:
            return res

        return {"nodes": res}

    def retrieveDocuments(self, documentIds):
        ln.warn("implement retrieveDocuments")
        return None

    def searchSimilar(self, docId):
        ln.warn("implement searchSimilar")
        return None
