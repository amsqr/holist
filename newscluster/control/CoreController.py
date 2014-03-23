from holist.util.util import *
ln = getModuleLogger(__name__)

from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.internet.threads import deferToThread
from holist.core.server.Listener import Listener

from newscluster.core.ClusterStrategy import ClusterStrategy
from holist.core.server.Listener import Listener

class CoreController(object):
	def __init__(self):
		self.listeners = []
		self.frontend = RESTfulFrontend(self)
		self.databaseInterface = DatabaseInterface()
		self.clusterStrategy = ClusterStrategy(self)

		reactor.run()

	def getClusters(self, json=True, full=False):
		return self.databaseInterface.getClusters(json, full)

	def updateClusters(self):
		#get new articles
		newDocuments = self.databaseInterface.getNewDocuments()
		#throw at clustering strategy
		self.clusterStrategy.handleDocuments(newDocuments)
		#notify that there's been a change
		self.notifyListeners()

	def onNewData(self):
		deferToThread(self.updateClusters)

	def registerListener(self, ip, port):
		listener = Listener(ip, port)
		self.listeners.append(listener)

	def saveCluster(self, cluster):
		self.databaseInterface.saveCluster(cluster)


	def notifyListeners(self):
		for listener in self.listeners:
			try:
				listener.notify()
			except:
				ln.error("couldn't notify listener")