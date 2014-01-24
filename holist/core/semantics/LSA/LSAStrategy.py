from holist.core.semantics.ISemanticsStrategy import ISemanticsStrategy
from gensim import models
import numpy

# SETTINGS
NUM_TOPICS = 100
CHUNKSIZE = 1000
DECAY = 0.8
DISTRIBUTED = False
ONEPASS = True

# MODEL CODE
class LSAStrategy(ISemanticsStrategy):
    NAME = "LSA"
    def __init__(self,corpus, dictionary, index, textIndex):
        """
        Initialize the model. This doesn't add any documents yet.
        """
        self.dictionary = dictionary
        self.index = index
        self.textIndex = textIndex
        self.corpus = corpus

        self.model = models.lsimodel.LsiModel(corpus=[doc.preprocessed for doc in corpus],num_topics=NUM_TOPICS, chunksize=CHUNKSIZE, id2word=self.dictionary,
            decay=DECAY, distributed=DISTRIBUTED, onepass=ONEPASS)

    @staticmethod
    def getNumFeatures():
        return NUM_TOPICS

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

        #update the documents
        for document in documents:
            document.vectors[self.NAME] = self.model[document.preprocessed]
        print "LSA: preprocessed documents, now updating index."
        for idx, document in enumerate(documents):
            if idx % 50 == 0:
                print "", idx, "..."
            # iterate through all documents for indexing
            for otherDoc in self.corpus:
                #add to index
                comp = self.compare([val for (k,val) in document.vectors[self.NAME]], 
                                    [val for (k,val) in otherDoc.vectors[self.NAME]]
                self.index.addEntry(document.id, otherDoc.id, comp))


    def __getitem__(self, item):
        return self.model[item]

    def queryText(self, textMinimalized, num_best):
        result = []
        plainTextSearchResults = self.textIndex.queryText(textMinimalized) # set of docIDs containing any words in the query
        textLSAVect = [val for (k,val) in self[textMinimalized]]

        for docId in  plainTextSearchResults:
            docLSAVect = [val for (k,val) in self.corpus[docId].vectors[self.NAME]]
            result.append((docId,self.compare(textLSAVect,docLSAVect))) #actual ranking determined by vecotr space similarity

        return sorted(result, key=lambda k: k[1], reverse=True)[:num_best]


    def queryId(self, docid):
        return self.index.query(docid)

    def compare(self, vec1, vec2, query=False):
        
    	#TODO consider adding this to the abstract base class
        
        #print "comparing: ", type(vec1), numpy.linalg.norm(vec2)
        dot = numpy.dot(vec1, vec2)
        return dot / (abs(numpy.linalg.norm(vec1)) * abs(numpy.linalg.norm(vec2)))


