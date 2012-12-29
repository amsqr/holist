from ..DatabaseInterface import DatabaseObject

class ProcessedArticle(DatabaseObject.DatabaseObject):
    def __init__(self, original, url, vector, organisations, individuals, locations):
        self.original = original #_id of the article that was processed
        self.sid = url
        self.vector = vector
        self.organisations = organisations
        self.individuals = individuals
        self.locations = locations

        self._id = None #this is the ID assigned by MongoDB
    def toDict(self):
        return {"original":self.original, "sid":self.sid,"vector": self.vector, "organisations": self.organisations, "individuals": self.individuals, "locations":self.locations}