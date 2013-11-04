import holist.core.semantics.ISemanticsStrategy
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
    def __init__(self, dictionary, index):
        """
        Initialize the model. This doesn't add any documents yet.
        """
        self.dictionary = dictionary
        self.index = index

        self.model = models.lsimodel.LsiModel(num_topics=NUM_TOPICS, chunksize=CHUNKSIZE, id2word=self.dictionary,
            decay=DECAY, distributed=DISTRIBUTED, onepass=ONEPASS)


    def handleDocuments(self, documents):
        """
        Add documents to the model, and update their vector representation fields.
        """
        #get minimalized forms
        minimalized = (doc.preprocessed for doc in documents)
        
        #update our model
        self.model.add_documents(minimalized)

        #update the documents
        for document in documents:
            document.representations[self.NAME] = self.model[document.preprocessed]

        #tell the index to update
        self.index.update(documents)

    def query(self, document):
        return self.index.query(document)

    def compare(self, doc1, doc2):
    	#TODO consider adding this to the abstract base class
    	vec1 = doc1.representations[self.NAME]
    	vec2 = doc2.representations[self.NAME]
        return (numpy.dot(vec1, vec2) / abs(numpy.linalg.norm(vec1) * numpy.linalg.norm(vec2)))


