__author__ = 'dowling'

from collections import defaultdict


class NamedEntityIndex(object):
    def __init__(self):
        """
        creates an inverted index:
            {named_entity -> [document_id]}
        """
        self.index = defaultdict(list)

    def addDocument(self, document):
        for namedEntity in document.vectors["NamedEntities"]:
            self.index[namedEntity].append(document._id)

    def query(self, namedEntity):
        return self.index[namedEntity]


