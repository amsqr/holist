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

# MODEL CODE
class LSAStrategy(ISemanticsStrategy):
    NAME = "LSA"
    def __init__(self,corpus, dictionary, load=False):
        """
        Initialize the model. This doesn't add any documents yet.
        """
        self.dictionary = dictionary
        self.corpus = corpus
        ln.info("initializing LSA model..")
        self.savename = self.NAME+"_"+"_".join([source.__class__.__name__ for source in  self.corpus.getDescription()]) 
        #[doc.preprocessed for doc in corpus]
        ln.debug("DICT size is %s, corpus size is %s", len(self.dictionary), len(self.corpus))
        self.model = models.lsimodel.LsiModel(corpus=None,num_topics=NUM_TOPICS, chunksize=CHUNKSIZE, id2word=self.dictionary,
            decay=DECAY, distributed=DISTRIBUTED, onepass=ONEPASS)
        
        import logging
        lsi_log = logging.getLogger("gensim.models.lsimodel")
        mat_log = logging.getLogger("gensim.matutils")
        
        lsi_log.setLevel(logging.INFO)
        mat_log.setLevel(logging.INFO)

        ln.info("LSA Initialized")

        """
        dispatcher.initialize(id2word=self.id2word, num_topics=num_topics,
                                      chunksize=chunksize, decay=decay,
                                      power_iters=self.power_iters, extra_samples=self.extra_samples,
                                      distributed=False, onepass=onepass)
        """

    @staticmethod
    def getNumFeatures():
        return NUM_TOPICS

    def computeVectorRepresentations(self, documents):
        for document in documents:
            document.vectors[self.NAME] = numpy.array([val for (k,val) in self.model[document.preprocessed]])

    def handleDocuments(self, documents):
        """
        Add documents to the model, and update their vector representation fields.
        """
        #get minimalized forms
        minimalized = (doc.preprocessed for doc in documents)

        #minimalized form is generally removed stop words, stemming, and then converted to BoW
        self.model.add_documents(minimalized)

        #add the document vector space representations
        self.computeVectorRepresentations(documents)


    def __getitem__(self, item):
        return self.model[item]


    def getOverview(self):
        return self.model.print_topics()

    def save(self):
        ln.debug("saving model")
        self.model.save("model_" + self.savename + ".lsa")
        ln.debug("saving index.")
        self.index.save("index_" + self.savename + ".idx")

    def load(self):
        ln.debug("loading model.")
        self.model = models.lsimodel.LsiModel.load("model_" + self.savename + ".lsa")
        ln.debug("loading index.")
        self.index.load("index_" + self.savename + ".idx")

