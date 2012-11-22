class DatabaseObject:
    def toDict(self):
        raise NotImplementedError("needs to be imlemented!")
    def __eq__(self, other):
        return self.sid == other.sid
    def __hash__(self):
        return hash(self.sid)