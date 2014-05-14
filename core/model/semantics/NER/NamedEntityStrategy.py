from core.util.util import *
ln = getModuleLogger(__name__)

from core.model.semantics.ISemanticsStrategy import ISemanticsStrategy

from nltk import sent_tokenize, word_tokenize, pos_tag, ne_chunk

import datetime

class NamedEntityStrategy(ISemanticsStrategy):
    NAME = "NamedEntities"
    def __init__(self):
        # this is where you would load a better model
        pass

    def getName(self):
        return self.NAME

    def extractEntities(seld, text):
        entities = []
        for sentence in sent_tokenize(text):
            chunks = ne_chunk(pos_tag(word_tokenize(sentence)))
            entities.extend([chunk for chunk in chunks if hasattr(chunk, 'node')])
        return list(set([(chunk.node, " ".join([x[0] for x in chunk.leaves()])) for chunk in entities]))

    def handleDocuments(self, docs, queue):
        ln.info("Extracting entities..")
        results = []
        for document in docs:
            entities = self.extractEntities(document.text)
            results.append((document, (self.NAME, entities)))
        ln.info("Done extracting entities.")
        queue.put((results, self))

    def load(self):
        raise Exception("Not implemented!")

    def save(self):
        raise Exception("Not implemented!")
