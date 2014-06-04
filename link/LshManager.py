__author__ = 'raoulfriedrich'

from lshash import LSHash
from core.model.semantics.LSA.LSAStrategy import NUM_TOPICS

NUMBER_OF_LSH_INDEXES = 3
NUMBER_OF_BITS_PER_HASH = 6

class LshManager(object):

    def __init__(self):

        self.lshIndexList = []

        # create a list of lsh indexes
        for x in xrange(NUMBER_OF_LSH_INDEXES):
            lsh = LSHash(NUMBER_OF_BITS_PER_HASH, NUM_TOPICS)
            self.lshIndexList.append(lsh)

    # adds a document to all lsh indexes
    def addDocument(self, document):

        lsa_vector = document.vectors["LSA"]

        dense_vector = self._sparseToDenseConverter(lsa_vector)

        database_id = document._id

        for x in self.lshIndexList:
            x.index(dense_vector, extra_data=database_id)

    # takes a document and returns database ids of similar documents
    # uses cosine function to determine similarity
    def getSimilarDocuments(self, document):

        lsa_vector = document.vectors["LSA"]

        dense_vector = self._sparseToDenseConverter(lsa_vector)

        resultSet = set()

        for x in self.lshIndexList:

            for result in x.query(dense_vector, num_results=10, distance_func="cosine"):
                resultSet.add(result[0][1])

        return list(resultSet)

    # converts a vector in sparse format to a vector in dense format
    def _sparseToDenseConverter(self, sparseVector):

        dense = {}
        for x in range(NUM_TOPICS):
            dense[x] = 0

        for dim, val in sparseVector:
            dense[dim] = val
        return [value for key, value in dense.items()]