from holist.DatabaseInterface import DatabaseObject

class WordType(DatabaseObject.DatabaseObject):
    def __init__(self, _id, token, frequency):
        self._id = _id
        self.sid = token
        self.frequency = frequency
    def toDict(self):
        return {"token":self.sid, "frequency":self.frequency}
