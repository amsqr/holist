from core.util.util import *
from legacy.newscluster.core import ClusterStrategy, DatabaseInterface
from legacy.newscluster.view import RESTfulFrontend

ln = getModuleLogger(__name__)

from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.internet.threads import deferToThread

from core.model.server.Listener import Listener

from core.util import config as holistConfig
from legacy.newscluster import config

import requests


class CoreController(object):
    def __init__(self):
        self.listeners = dict()
        self.frontend = RESTfulFrontend(self)
        self.databaseInterface = DatabaseInterface()
        self.clusterStrategy = ClusterStrategy(self)

        self.connected = False
        self.loop = LoopingCall(self.connectToCore)
        self.loop.start(3)

        reactor.run()

    def connectToCore(self):
        try:
            data = {"ip": config.clusterapiurl,"port": config.clusterapiport}
            res = requests.post("http://" + holistConfig.holistcoreurl +":"+ str(holistConfig.holistcoreport) +"/register_listener", data=data )
            if success:
                ln.info("successfully connected to model")
                self.loop.stop()
        except Exception, e:
            ln.error(str(e))

    def getClusters(self, json=True, full=False):
        return self.databaseInterface.getClusters(json, full)

    def updateClusters(self, ids):
        ln.debug("updating clusters.")
        #get new articles
        newDocuments = self.databaseInterface.getNewDocuments(ids)
        #throw at clustering strategy
        self.clusterStrategy.handleDocuments(newDocuments)

        #TODO
        ids = []

        #notify that there's been a change
        ln.debug("notifying listeners")
        self.notifyListeners(ids)

    def onNewData(self, ids):
        deferToThread(self.updateClusters, ids)

    def registerListener(self, ip, port):
        listener = Listener(ip, port)
        self.listeners[ip+":"+str(port)] = listener

    def saveCluster(self, cluster):
        self.databaseInterface.saveCluster(cluster)

    def notifyListeners(self, ids):
        for listener in self.listeners.values():
            try:
                listener.notify(ids)
            except:
                ln.error("couldn't notify listener %s", listener.ip+":"+str(listener.port))