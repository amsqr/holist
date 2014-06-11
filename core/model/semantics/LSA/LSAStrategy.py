from core.model.server import NodeCommunicator
from core.util.util import *
ln = getModuleLogger(__name__)


from core.util import config

from core.model.semantics.ISemanticsStrategy import ISemanticsStrategy
from core.model.preprocess.TokenizingPorter2Stemmer import TokenizingPorter2Stemmer
from core.model.dictionary.hash.HashDictionary import HashDictionary
from core.model.server.NodeCommunicator import NodeCommunicator
from gensim import models
import itertools

from twisted.internet import reactor
from twisted.internet.threads import deferToThread
from twisted.internet.task import LoopingCall

from Queue import Queue

CORE_IP = "localhost"
REGISTER_PORT = config.strategyregisterport
LISTEN_PORT = config.lsa_strategy_port

# SETTINGS
NUM_TOPICS = 200
CHUNK_SIZE = 1000
DECAY = 0.8
DISTRIBUTED = False
ONE_PASS = True

DICTIONARY = HashDictionary


def silenceGensim():
        import logging
        lsi_log = logging.getLogger("gensim.models.lsimodel")
        mat_log = logging.getLogger("gensim.matutils")

        lsi_log.setLevel(logging.INFO)
        mat_log.setLevel(logging.INFO)


class LSAStrategy(ISemanticsStrategy):
    NAME = "LSA"

    def __init__(self):
        """
        Initialize the model. This doesn't add any documents yet.
        """
        silenceGensim()

        self.dictionaries = dict()
        self.preprocessor = TokenizingPorter2Stemmer()

        #this dict keeps a model for every source type
        #  (since e.g. RSS feeds should be treated separately from twitter feeds)
        self.models = dict()

        #this dict keeps a dictionary for every source type 
        self.dictionaries = dict()

        self.queue = Queue()
        self.modelQueue = Queue()
        self.nodeCommunicator = NodeCommunicator(self, LISTEN_PORT)
        self.nodeCommunicator.registerWithNode(CORE_IP, REGISTER_PORT)  # register this node with the core

        ln.info("LSA Initialized")
        self.updating = False
        loop = LoopingCall(self.update)
        loop.start(10)

        reactor.run()

    def createDictionary(self, sourceType):
        ln.info("creating a new dictionary for sourceType %s.", sourceType)
        dictionary = DICTIONARY()
        self.dictionaries[sourceType] = dictionary
        return dictionary

    def createModel(self, sourceType, dictionary):
        ln.info("creating a new LSA model for sourceType %s.", sourceType)
        model = models.lsimodel.LsiModel(corpus=None, num_topics=NUM_TOPICS, chunksize=CHUNK_SIZE, id2word=dictionary,
                                         decay=DECAY, distributed=DISTRIBUTED, onepass=ONE_PASS)
        self.models[sourceType] = model
        return model

    def queueDocuments(self, returnTo, documents, relabel):
        self.queue.put((returnTo, documents, relabel))

    def update(self):
        deferToThread(self.__update())

    def __update(self):
        if self.updating:
            return

        self.updating = True
        if not self.queue.empty():
            returnTo, docs, relabel = self.queue.get()
            self._handleDocuments(returnTo, docs, relabel)
        self.updating = False



    def _handleDocuments(self, returnTo, docs, relabel=False):
        """
        Add documents to the model, and send back their vector representations.
        """
        ln.info("LSA tasked with %s documents.", len(docs))
        self.load()

        documents = []
        for docDict in docs:
            document = Document("")
            document.__dict__ = docDict
            documents.append(document)

        documentGroups = itertools.groupby(documents, lambda d: d.sourceType)
        results = []
        for sourceType, iterator in documentGroups:
            documents = list(iterator)

            #retrieve the dict and LSA model for this source, or create new ones

            dictionary = self.dictionaries.get(sourceType, None)
            if dictionary is None:
                dictionary = self.createDictionary(sourceType)

            model = self.models.get(sourceType, None)
            if model is None:
                model = self.createModel(sourceType, dictionary)


            for doc in documents:
                self.preprocessor.preprocess(doc, dictionary)

            prep = (doc.preprocessed for doc in documents)

            if not relabel or model.projection.u is None:
                model.add_documents(prep)

            # add the document vector space representations
            sourceTypeTag = self.NAME  # +"_"+document.sourceType

            results += [{"_id": document._id, "strategy": sourceTypeTag, "vector": model[document.preprocessed]}
                        for document in documents]
        self.save()
        self.nodeCommunicator.respond(returnTo, {"vectors": results})

    def handleOne(self, text, sourceType="RSSFeed"):
        if not self.models:
            self.load()

        dictionary = self.dictionaries.get(sourceType, None)
        if dictionary is None:
            dictionary = self.createDictionary(sourceType)

        text = self.preprocessor.preprocess(text, dictionary)
        res = {"vectors": []}
        for modelName in self.models:
            res["vectors"].append(
                {
                    "_id": None,
                    "vector": self.models[modelName][text],
                    "strategy": "LSA_" + modelName
                }
            )
        return res

    def save(self):
        ln.debug("saving models")
        for sourceType in self.models:
            model = self.models[sourceType]
            model.save("persist/model_" + sourceType + ".lsa")
        ln.debug("done saving models")

    def load(self):
        ln.debug("Loading models..")
        import os
        for filename in os.listdir(os.getcwd()+"/persist"):
            if filename.endswith(".lsa"):
                loadfilename = "persist/"+filename
                model = models.lsimodel.LsiModel.load(loadfilename)
                sourceType = filename[6:-4]
                self.models[sourceType] = model
                ln.info("loaded model %s for sourceType %s", filename, sourceType)
        ln.debug("Done loading models.")


NUM_TRAIN = 500


class CustomLsiModel(models.lsimodel.LsiModel):
    # TODO make this work
    def __init__(self, corpus, num_topics, chunksize, id2word, decay, distributed, onepass):
        super(CustomLsiModel, self).__init__(corpus=corpus, num_topics=num_topics, chunksize=chunksize, id2word=id2word,
                                             decay=decay, distributed=distributed, onepass=onepass)
        self._currentChunk = []
        self._numTrained = 0

    def add_documents(self, documents):
        self._currentChunk += documents
        chunkSize = len(self._currentChunk)
        if self._numTrained < NUM_TRAIN:
            ln.debug("Training LSI model in foreground")
            super(CustomLsiModel, self).add_documents(self._currentChunk)
            self._numTrained += chunkSize
        elif chunkSize > CHUNK_SIZE:
            ln.debug("Training LSI model in background")
            self._updateInBackground()

    def _updateInBackground(self):
        if self._updating:
            return
        self._updating = True
        deferToThread(super(CustomLsiModel, self).add_documents, self._currentChunk[:])
        self._currentChunk = []
        self._updating = False

