__author__ = 'dowling'

from core.util.util import *
ln = getModuleLogger(__name__)

from collections import defaultdict


class NamedEntityIndex(object):
    def __init__(self):
        """
        creates an inverted index:
            {named_entity -> [document_id]}
        """
        self.index = defaultdict(list)

    def addDocument(self, document):
        for entityType, namedEntity in document.vectors["named_entities"]:
            self.index[namedEntity].append(document._id)

    def query(self, namedEntity):
        return self.index[namedEntity]


