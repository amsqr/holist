__author__ = 'raoulfriedrich'

from lshash import LSHash
from core.model.semantics.LSA.LSAStrategy import NUM_TOPICS

NUMBER_OF_LSH_INDEXES = 3
NUMBER_OF_BITS_PER_HASH = 6

class LshManager(object):

    def __init__(self):

        self.lshIndexList = []

        for x in xrange(NUMBER_OF_LSH_INDEXES):
            lsh = LSHash(NUMBER_OF_BITS_PER_HASH, NUM_TOPICS)
            self.lshIndexList.append(lsh)

        #addDocument()

    # adds a document to all lsh indexes
    def addDocument(self, document):

        lsa_vector = document.vectors["LSA"]

        dense = {}
        for x in range(200):
            dense[x] = 0

        for dim, val in lsa_vector:
            dense[dim] = val
        dense_vector = [value for key, value in dense.items()]

        database_id = document._id

        for x in self.lshIndexList:
            x.index(dense_vector, extra_data=database_id)