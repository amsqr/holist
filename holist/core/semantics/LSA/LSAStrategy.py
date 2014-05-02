from holist.util.util import *
ln = getModuleLogger(__name__)

from holist.core.semantics.ISemanticsStrategy import ISemanticsStrategy
from holist.core.preprocess.TokenizingPorter2Stemmer import TokenizingPorter2Stemmer
from holist.core.dictionary.hash.HashDictionary import HashDictionary
from gensim import models
import numpy
import datetime
import time
import itertools


# SETTINGS
NUM_TOPICS = 100
CHUNKSIZE = 1000
DECAY = 0.8
DISTRIBUTED = False
ONEPASS = True

DICTIONARY = HashDictionary

class LSAStrategy(ISemanticsStrategy):
    NAME = "LSA"
    def __init__(self):
        """
        Initialize the model. This doesn't add any documents yet.
        """
        self.dictionaries = dict()
        self.preprocessor = TokenizingPorter2Stemmer()

        #this dict keeps a model for every source type (since e.g. RSS feeds should be treated seperately from twitter feeds)
        self.models = dict()
        #this dict keeps a dictionary for every source type 
        self.dictionaries = dict()

        self.silenceGensim()

        ln.info("LSA Initialized")

    def silenceGensim(self):
        import logging
        lsi_log = logging.getLogger("gensim.models.lsimodel")
        mat_log = logging.getLogger("gensim.matutils")
        
        lsi_log.setLevel(logging.INFO)
        mat_log.setLevel(logging.INFO)

    @staticmethod
    def getNumFeatures():
        return NUM_TOPICS

    def createDictionary(self, sourceType):
        ln.info("creating a new dictionary for sourceType %s.", sourceType)
        dictionary =  DICTIONARY()
        self.dictionaries[sourceType] = dictionary
        return dictionary

    def createModel(self, sourceType, dictionary):
        ln.info("creating a new LSA model for sourceType %s.", sourceType)
        model = models.lsimodel.LsiModel(corpus=None,num_topics=NUM_TOPICS, chunksize=CHUNKSIZE, id2word=dictionary,
                decay=DECAY, distributed=DISTRIBUTED, onepass=ONEPASS)
        self.models[sourceType] = model
        return model

    def handleDocuments(self, docs, queue):
        """
        Add documents to the model, and update their vector representation fields.
        """
        
        documentGroups = itertools.groupby(docs, lambda d: d.sourceType)
        results = []
        for sourceType, iterator in documentGroups:
            documents = list(iterator)

            #retrieve the sict and LSA model for this source, or create new ones
            dictionary = self.dictionaries.get(sourceType, self.createDictionary(sourceType))
            model = self.models.get(sourceType, self.createModel(sourceType, dictionary))

            for doc in documents:
                self.preprocessor.preprocess(doc, dictionary)
            #get minimalized documents (removed stop words, stemming, and then converted to BoW)
            minimalized = (doc.preprocessed for doc in documents)
                        
            model.add_documents(minimalized)

            #add the document vector space representations
            results += [(document, (self.NAME+"_"+document.sourceType, [val for (k,val) in model[document.preprocessed]])) for document in documents]
        queue.put((results, self))

    def getOverview(self):
        return self.model.print_topics()

    def save(self):
        ln.debug("saving models")
        for sourceType in self.models:
            model = self.models[sourceType]
            model.save("model_" + sourceType + ".lsa")
        ln.debug("done saving models")

    def load(self):
        ln.debug("Loading models..")
        import os
        for filename in os.listdir(os.getcwd()):
            if filename[-4:] == ".lsa":
                model = models.lsimodel.LsiModel.load(filename)
                sourceType = filename[6:-4]
                self.models[sourceType] = model
                ln.info("loaded model %s for sourceType %s", filename, sourceType)
        ln.debug("Done loading models.")

