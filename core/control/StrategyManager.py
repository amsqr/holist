from core.util.util import *
ln = getModuleLogger(__name__)

from core.util import config

from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.internet import reactor
import requests
import json
import cgi

from Queue import Queue


class RegisterStrategy(Resource):

    def __init__(self, manager):
        self.manager = manager

    def render_POST(self, request):
        ln.debug("received registration request: %s", request.args)
        ip = cgi.escape(request.args["ip"][0])
        port = cgi.escape(request.args["port"][0])
        name = cgi.escape(request.args["strategy"][0])
        if None not in (ip, port):
            self.manager.registerStrategy(name, ip, port)
            return json.dumps({"result": "success"})
        else:
            return json.dumps({"result": "failure"})


class Strategy(object):
    def __init__(self, name, ip, port):
        self.name = name
        self.ip = ip
        self.port = port


class StrategyCallback(Resource):

    def __init__(self, manager):
        self.manager = manager

    def render_POST(self, request):
        data = request.content.read()
        ln.debug("got response data: %s...", data[:1000])
        try:
            data = json.loads(data)
        except:
            ln.warn("Couldn't parse strategy callback: %s...", data[:5000])
            return 0

        vectors = data["vectors"]
        self.manager.queueCallback(vectors)
        return json.dumps({"result": "ok"})


class StrategyManager(object):

    def __init__(self, controller):
        self.resultQueue = Queue()
        self.controller = controller
        self.strategies = []
        self.setupResources()  # start listening

    def setupResources(self):
        root = Resource()
        registerPage = RegisterStrategy(self)
        callbackPage = StrategyCallback(self)
        root.putChild("register_strategy", registerPage)
        root.putChild("callback", callbackPage)
        factory = Site(root)
        reactor.listenTCP(config.strategyregisterport, factory)

    def queueCallback(self, results):
        self.resultQueue.put(results)

    def registerStrategy(self, name, ip, port):
        strategy = Strategy(name, ip, port)
        self.strategies.append(strategy)

    def handle(self, documents):
        docDicts = []
        for document in documents:  # serialize object ids
            docDict = document.__dict__
            docDict["_id"] = str(document._id)
            docDicts.append(docDict)

        taskData = {"respondTo": "http://localhost:"+str(config.strategyregisterport)+"/callback",
                    "documents": docDicts}

        docIndex = dict()
        for doc in documents:
            docIndex[str(doc._id)] = doc

        waitFor = 0
        for strategy in self.strategies:
            #todo: error handling. if a strategy is not responsive, then remove it.
            requests.post("http://"+strategy.ip+":"+str(strategy.port)+"/task", json.dumps(taskData))
            waitFor += 1

        results = []
        received = 0
        while received < waitFor:
            ln.debug("waiting to get results from queue..")
            vectors = self.resultQueue.get(True)
            results.append(vectors)
            received += 1
            ln.debug("got %s out of %s results from queue.", received, waitFor)

        ln.debug("Got all results. Merging.. ")
        for strategyResults in results:  # merge vectors back into documents
            for result in strategyResults:
                docId = result["_id"]
                vector = result["vector"]
                strategy = result["strategy"]

                document = docIndex[docId]
                document.vectors[strategy] = vector

        allResults = docIndex.values()

        return allResults


