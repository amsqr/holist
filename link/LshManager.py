__author__ = 'raoulfriedrich'

from lshash import LSHash

NUMBER_OF_LSH_INDEXES = 3

class LshManager(object):

    def __init__(self):

        self.lshIndexList = []

        for x in xrange(NUMBER_OF_LSH_INDEXES):
            lsh = LSHash(6, 200)
            self.lshIndexList.append(lsh)


    # adds a lsa vector to all lsh indexes
    def addVector(self, lsaVector):

        for x in self.lshIndexList:
            x.index(lsaVector)