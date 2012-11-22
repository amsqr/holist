from ..DatabaseInterface import DatabaseObject

class Term(DatabaseObject.DatabaseObject):
	def __init__(self, id, term, occurrences):
		self._id = None
		self.sid = term
		self.occurrences = occurrences
	def toDict(self):
        return {"term":self.sid, "occurrences":self.occurrences}
