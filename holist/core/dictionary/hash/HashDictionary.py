from gensim.corpora.hashdictionary import HashDictionary as HashDict

class HashDictionary(HashDict):
	def __init__(self):
		super(HashDictionary, self).__init__(id_range=200003)