from backend.core.util.util import *
ln = getModuleLogger(__name__)

__author__ = 'raoulfriedrich'

from lshash import LSHash
import redis
import json
import ast
from backend.core.model.semantics.LSA.LSAStrategy import NUM_TOPICS
from backend.link.LinkController import bsonToClientBson
import datetime

NUMBER_OF_LSH_INDEXES = 10
NUMBER_OF_BITS_PER_HASH = 6
DUPLICATE_SIMILARITY_THRESHOLD = 0.98

class Document:
    pass

class LshManager(object):

    def __init__(self):
        self.lshIndexList = []


        # create a list of lsh indexes
        self.lsh = LSHash(NUMBER_OF_BITS_PER_HASH, NUM_TOPICS, num_hashtables=NUMBER_OF_LSH_INDEXES,
                          storage_config={"redis": {"host": "localhost", "port": 6379}})

    def clearIndex(self):
        redis.Redis().flushall()

    # adds a document to all lsh indexes
    def addDocument(self, document):
        lsa_vector = document.vectors["LSA"]

        dense_vector = self._sparseToDenseConverter(lsa_vector)

        if not hasattr(document, "timestamp"):
            document.timestamp = str(datetime.datetime.now())

        extra = json.dumps(str(document._id))

        # detect duplicates
        nearest = self.lsh.query(dense_vector, num_results=1, distance_func="cosine")[0]
        if nearest[1] > DUPLICATE_SIMILARITY_THRESHOLD:
            extra = ast.literal_eval(ast.literal_eval(nearest[0])[1])
            ln.warn("Detected duplicate for %s (ID %s): %s.", document.title, document._id, extra)
        else:
            self.lsh.index(dense_vector, extra_data=extra)  # extra MUST be hashable

    # takes a document and returns database ids of similar documents
    # uses cosine function to determine similarity
    def getSimilarDocuments(self, document):
        if isinstance(document, Document):
            lsa_vector = document.vectors["LSA"]
        else:
            lsa_vector = document

        dense_vector = self._sparseToDenseConverter(lsa_vector)

        client = getDatabaseConnection()

        resultSet = set()
        results = []

        for result in self.lsh.query(dense_vector, num_results=25, distance_func="cosine"):
            # example:
            # [
            #   (((1, 2, 3), "{'extra1':'data'}"), 0),
            #   (((1, 1, 3), "{'extra':'data'}"), 1)
            # ]
            extra = ast.literal_eval(ast.literal_eval(result[0])[1])

            clientDoc = bsonToClientBson(client.holist.articles.find({"_id": extra}).next())
            clientDoc['lsa'] = self._sparseToDenseConverter(clientDoc['lsa'])
            jsonstr = json.dumps(clientDoc)

            if not jsonstr in resultSet:
                resultSet.add(jsonstr)
                results.append(clientDoc)

        ln.debug("retrieved %s documents.", len(results))
        return results

    # converts a vector in sparse format to a vector in dense format
    def _sparseToDenseConverter(self, sparseVector):
        dense = {}
        for x in range(NUM_TOPICS):
            dense[x] = 0

        for dim, val in sparseVector:
            dense[dim] = val
        return [value for key, value in dense.items()]