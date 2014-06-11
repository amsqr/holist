__author__ = 'dowling'

from core.util.util import *
ln = getModuleLogger(__name__)

from collections import defaultdict

import ast

class NamedEntityIndex(object):
    def __init__(self):
        """
        creates an inverted index:
            {named_entity -> [document_id]}
        """
        self.index = defaultdict(list)
        try:
            self.load()
        except:
            ln.debug("Couldn't load index from file.")

    def addDocument(self, document):
        for entityType, namedEntity in document.vectors["named_entities"]:
            self.index[namedEntity].append(document._id)

    def query(self, namedEntity):
        return self.index[namedEntity]

    def save(self):
        with open("./persist/NERIndex.idx", "w") as f:
            f.write(str(self.index))

    def load(self):
        with open("./persist/NERIndex.idx", "r") as f:
            self.index = ast.literal_eval(f.read())


