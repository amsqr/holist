import heapq
import numpy
import itertools

def cosine(vec1, vec2):
    return (numpy.dot(vec1, vec2) / abs(numpy.linalg.norm(vec1) * numpy.linalg.norm(vec2)))

def harmonicMean(a,b):
    return 2*a*b / (a + b)

class DocumentIndex(object):
    def __init__(self):
        self._index = {}
        self.documents = []

    def add(self, document):
        heapq.heappush(self.documents, (document.timestamp,document))
        self._index[document.id] = []

        #get the last config.indexCompareLast number of documents
        for otherDocument in heapq.nlargest(config.indexCompareLast, self.documents):
            otherDocument = otherDocument[1]
            
            #compute the cosine similarity between the added document
            similarity = cosine(document.vector, otherDocument.vector)

            self._handleSimilarity(similarity, document, otherDocument)
            self._handleSimilarity(similarity, otherDocument, document)
            

    def _handleSimilarity(self, doc1, doc2, similarity):
        if similarity > max(self._index[doc1.id], key=(lambda item: item[0]))
            heapq.heappush(self._index[doc1.id], (similarity, doc2))
            if len(self._index[doc1.id]) > config.indexKeepTop:
                #slice the list to the top k similar documents
                self._index[doc1.id] = [heapq.heappop(self._index[doc1.id]) for x in range(config.indexKeepTop) ]

    def retrieveMatchesBySourceDissimilarity(self, id, source):
        return sorted(self._index[id], 
            key=(
                lambda item: 
                    harmonicMean( item[0], 
                        cosine( source.vector, item[1].source.vector))))
    
    def retrieveMatchesById(self, id):
        return sorted(self._index[id], key=(lambda i: i[0]))