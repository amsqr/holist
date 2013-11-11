from holist.core.semantics.ISemanticsStrategy import ISemanticsStrategy
from gensim import models

# SETTINGS
NUM_TOPICS = 100
CHUNKSIZE = 1000
DECAY = 0.8
DISTRIBUTED = False
ONEPASS = True

# MODEL CODE
class LSAStrategy(ISemanticsStrategy):
    NAME = "LSA"
    def __init__(self,corpus, dictionary, index):
        """
        Initialize the model. This doesn't add any documents yet.
        """
        self.dictionary = dictionary
        self.index = index

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
        print "DEBUG: ", list(minimalized)[0]
        #update our model
        #if self.model.projection.u is None:
        #    self.model.projection = gensim.models.lsimodel.Projection(NUM_TOPICS)
        self.model.add_documents(minimalized)

        #update the documents
        for document in documents:
            document.vectors[self.NAME] = self.model[document.preprocessed]

        #tell the index to update
        self.index.addDocuments(documents)

    def __getitem__(self, item):
        return self.model[item]

    def queryText(self, text, num_best):
        return self.index.queryText(text, num_best)

    def queryDocId(self, docid):
        return self.index.queryById(docid, num_best)


    def compare(self, doc1, doc2):
    	#TODO consider adding this to the abstract base class
    	vec1 = doc1.vectors[self.NAME]
    	vec2 = doc2.vectors[self.NAME]
        return (numpy.dot(vec1, vec2) / abs(numpy.linalg.norm(vec1) * numpy.linalg.norm(vec2)))


