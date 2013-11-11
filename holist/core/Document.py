class Document(object):
	def __init__(self,text):
		self.text = text
		self.id = None
		self.preprocessed = []
		self.vectors = dict()
	def __iter__(self):
		for id, token in self.preprocessed:
			yield token

	def __len__(self):
		return len(self.preprocessed)