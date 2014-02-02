from holist.util.util import *
ln = getModuleLogger(__name__)

from holist.core.semantics.ISemanticsStrategy import ISemanticsStrategy
from gensim import models
import numpy
import datetime

# SETTINGS
NUM_TOPICS = 100
CHUNKSIZE = 1000
DECAY = 0.8
DISTRIBUTED = False
ONEPASS = True

# MODEL CODE
class LSAStrategy(ISemanticsStrategy):
    NAME = "LSA"
    def __init__(self,corpus, dictionary, index, textIndex, load=False):
        """
        Initialize the model. This doesn't add any documents yet.
        """
        self.dictionary = dictionary
        self.index = index
        self.textIndex = textIndex
        self.corpus = corpus
        ln.info("initializing LSA model..")
        self.savename = self.NAME+"_"+"_".join([source.__class__.__name__ for source in  self.corpus.getDataSources()]) 
        #[doc.preprocessed for doc in corpus]
        self.model = models.lsimodel.LsiModel(corpus=None,num_topics=NUM_TOPICS, chunksize=CHUNKSIZE, id2word=self.dictionary,
            decay=DECAY, distributed=DISTRIBUTED, onepass=ONEPASS)
        ln.info("LSA Initialized")

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

        #minimalized form is usually removed stop words, stemming, and then converted to BoW
        #print "DEBUG: ", list(minimalized)[0]
        #update our model
        #if self.model.projection.u is None:
        #    self.model.projection = gensim.models.lsimodel.Projection(NUM_TOPICS)
        self.model.add_documents(minimalized)

        #add the document vector space representations
        self.computeVectorRepresentations(documents)
        self.indexDocuments(documents)

    def indexDocuments(self, documents):
        ln.debug("LSA: processed documents, now updating index. Processing a total of %s documents." % len(documents))
        if self.corpus.isStatic():
            documents = sorted(documents,key=lambda doc: doc.id)

        
        for idx, document in enumerate(documents):
            if idx % 100 == 0:
                ln.debug("indexed %s documents..." % idx)

            # iterate through all documents for indexing
            relevantDocs = self.textIndex.queryText(document.preprocessed)
            if self.corpus.isStatic(): #optimization step if we can create a global ordering
                relevantDocs = sorted(relevantDocs)

            for otherDocId in relevantDocs:
                if self.corpus.isStatic() and otherDocId <= document.id:
                    continue
                otherDoc = self.corpus[otherDocId]
                #add to index
                comp = self.compare(document.vectors[self.NAME], otherDoc.vectors[self.NAME])

                self.index.addEntry(document.id, otherDoc.id, comp)
                if self.corpus.isStatic():
                    self.index.addEntry(otherDoc.id, document.id, comp)


    def __getitem__(self, item):
        return self.model[item]

    def queryText(self, textMinimalized, num_best):
        result = []
        plainTextSearchResults = self.textIndex.queryText(textMinimalized) # set of docIDs containing any words in the query
        textLSAVect = [val for (k,val) in self[textMinimalized]]

        for docId in  plainTextSearchResults:
            docLSAVect = self.corpus[docId].vectors[self.NAME]
            result.append((docId,self.compare(textLSAVect,docLSAVect))) #actual ranking determined by vecotr space similarity

        return sorted(result, key=lambda k: k[1], reverse=True)[:num_best]


    def queryId(self, docid):
        return self.index.query(docid)

    def compare(self, vec1, vec2, query=False):
        dot = numpy.dot(vec1, vec2)
        return dot / (abs(numpy.linalg.norm(vec1)) * abs(numpy.linalg.norm(vec2)))

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

