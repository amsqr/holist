from holist.util.util import *
ln = getModuleLogger(__name__)

from holist.core.semantics.ISemanticsStrategy import ISemanticsStrategy
from gensim import models
import numpy
import datetime
import time

# SETTINGS
NUM_TOPICS = 100
CHUNKSIZE = 1000
DECAY = 0.8
DISTRIBUTED = False
ONEPASS = True


class LSAStrategy(ISemanticsStrategy):
    NAME = "LSA"
    def __init__(self, dictionary):
        """
        Initialize the model. This doesn't add any documents yet.
        """
        self.dictionary = dictionary
        
        #this dict keeps a model for every source type (since e.g. RSS feeds should be treated seperately from twitter feeds)
        self.models = dict()
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

    def computeVectorRepresentations(self, documents):
        for document in documents:
            document.vectors[self.NAME+"_"+document.sourceType] = [val for (k,val) in self.model[document.preprocessed]]

    def handleDocuments(self, docs):
        """
        Add documents to the model, and update their vector representation fields.
        """
        documentGroups = itertools.groupby(docs, lambda d: d.sourceType)
        for sourceType in documentGroups:
            #retrieve the LSA model for this source
            model = self.models.get(sourceType, None)
            if model == None:
                ln.info("creating a new LSA model for sourceType %s.", sourceType)
                model = models.lsimodel.LsiModel(corpus=None,num_topics=NUM_TOPICS, chunksize=CHUNKSIZE, id2word=self.dictionary,
                            decay=DECAY, distributed=DISTRIBUTED, onepass=ONEPASS)
                self.models[sourceType] = model

            documents = documentGroups[sourceType]

            #get minimalized documents (removed stop words, stemming, and then converted to BoW)
            minimalized = (doc.preprocessed for doc in documents)
            
            
            self.model.add_documents(minimalized)

            #add the document vector space representations
            self.computeVectorRepresentations(documents)


    def __getitem__(self, item):
        return self.model[item]


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

