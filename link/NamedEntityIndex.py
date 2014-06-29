__author__ = 'dowling'

from core.util.util import *
ln = getModuleLogger(__name__)

from collections import defaultdict

import ast

class NamedEntityIndex(object):
    def __init__(self):
        """
        creates an inverted index:
            {named_entity -> [(document_id, frequency)]}
        """
        self.index = defaultdict(list)
        try:
            self.load()
        except:
            ln.debug("Couldn't load index from file.")

    def addDocument(self, document):
        counts = self.countEntities(document.vectors["named_entities"])
        for namedEntity, count in counts.items():
            self.index[namedEntity].append((document._id, count))

    def countEntities(self, entities):
        entityCounts = defaultdict(int)
        for idx, (entityType, entity) in enumerate(entities):
            # first, update the raw count of this entity
            entityCounts[entity] += 1

            # next, see if this entity might be equivalent to any of the previous entities
            for otherEntityType, otherEntity in entities[:idx]:
                parts = otherEntity.split(" ")
                # if the entity is a true subset of another entity, increment the frequency for the other one as well
                # This lets us better resolve situations where a person is mentioned (Firstname, Lastname),
                # but subsequently only mentioned by last name.
                # This also helps with organizations (Apple vs. Apple Computers).
                if len(parts) != 1 and entity in parts:
                    entityCounts[otherEntity] += 1

        return entityCounts

    def query(self, namedEntity):
        return self.index[namedEntity]

    def save(self):
        with open("./persist/NERIndex.idx", "w") as f:
            f.write(str(dict(self.index)))

    def load(self):
        with open("./persist/NERIndex.idx", "r") as f:
            index = ast.literal_eval(f.read())
            self.index = defaultdict(list)
            for entry in index:
                self.index[entry] = index[entry]



