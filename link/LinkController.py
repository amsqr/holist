__author__ = 'raoulfriedrich'

from core.util.util import *

import logging
import requests
import json

logging.basicConfig(format=config.logFormat, level=logging.DEBUG if config.showDebugLogs else logging.INFO)
ln = getModuleLogger(__name__)

from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from link.api.RESTfulApi import RESTfulApi
from core.model.server.NodeCommunicator import NodeCommunicator
from link.LshManager import LshManager

CORE_IP = "localhost"
REGISTER_PORT = config.holistcoreport
LISTEN_PORT = config.strategyregisterport + 14


class LinkController(object):

    def __init__(self):
        self.nodeCommunicator = NodeCommunicator(self, LISTEN_PORT)
        self.nodeCommunicator.registerWithNode(CORE_IP, REGISTER_PORT)

        self.lshManager = LshManager()

        self.frontend = RESTfulApi(self)

        ln.info("running reactor.")
        reactor.run()

    def subscribe(self):

        try:
            ln.info("attempting to subscribe to core node at %s:%s",config.holistcoreurl, config.holistcoreport)

            # my ip and port for callback
            data = {"ip":config.link_node_ip, "port":config.link_node_port}

            # create http post
            res = requests.post("http://"+config.holistcoreurl+":"+str(config.holistcoreport)+"/register_listener", data=data)
            success = json.loads(res.text)["result"] == "success"

            ln.info("successfully subscribed.")
            return success

        except Exception, e:
            ln.warn("couldn't subscribe: %s", str(e))
            return False

    def handleNewDocuments(self, newDocuments):
        documents = []
        for docDict in newDocuments:
            document = Document()
            document.__dict__ = docDict
            documents.append(document)


    def performEntitySearch(self, entityName):
        ln.warn("implement performEntitySearch")
        return None

    def retrieveDocuments(self, documentIds):
        ln.warn("implement retrieveDocuments")
        return None

    def searchSimilar(self, docId):
        ln.warn("implement searchSimilar")
        return None
