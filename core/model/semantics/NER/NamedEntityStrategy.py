from core.model.server import NodeCommunicator
from core.util.util import *
ln = getModuleLogger(__name__)


from core.model.semantics.ISemanticsStrategy import ISemanticsStrategy
from core.model.server.NodeCommunicator import NodeCommunicator

from nltk import sent_tokenize, word_tokenize, pos_tag, ne_chunk

from Queue import Queue

from twisted.internet import reactor
from twisted.internet.task import LoopingCall


CORE_IP = "localhost"
REGISTER_PORT = config.strategyregisterport

LISTEN_PORT = config.strategyregisterport + 4


class Document: pass


class NamedEntityStrategy(ISemanticsStrategy):
    NAME = "NamedEntities"

    def __init__(self):
        self.nodeCommunicator = NodeCommunicator(self, LISTEN_PORT)
        self.nodeCommunicator.registerWithNode(CORE_IP, REGISTER_PORT)  # register this node with the core

        self.queue = Queue()

        self.updating = False
        loop = LoopingCall(self.update)
        loop.start(10)

        reactor.run()

    def queueDocuments(self, returnTo, documents):
        self.queue.put((returnTo, documents))

    def update(self):
        if self.updating:
            return

        self.updating = True
        if not self.queue.empty():
            returnTo, docs = self.queue.get()
            self._handleDocuments(returnTo, docs)
        self.updating = False

    def _handleDocuments(self, returnTo, docs):
        ln.info("NER tasked with %s documents.", len(docs))
        documents = []
        for docDict in docs:
            document = Document()
            document.__dict__ = docDict
            documents.append(document)

        ln.info("Extracting entities..")
        count = 0
        results = []
        for doc in documents:
            count += 1
            if count % 50 == 0:
                ln.debug("extracted %s documents. now handling was id:%s", count, doc._id)
            entities = self.extractEntities(doc.text)
            results.append({"_id": doc._id, "strategy": "named_entities", "vector": entities})

        ln.info("Done extracting entities.")

        self.nodeCommunicator.respond(returnTo, {"vectors": results})

    def extractEntities(self, text):
        entities = []
        for sentence in sent_tokenize(text):
            chunks = ne_chunk(pos_tag(word_tokenize(sentence)))
            entities.extend([chunk for chunk in chunks if hasattr(chunk, 'node')])
        return list(set([(chunk.node, " ".join([x[0] for x in chunk.leaves()])) for chunk in entities]))


    def load(self):
        raise Exception("Not implemented!")

    def save(self):
        raise Exception("Not implemented!")
