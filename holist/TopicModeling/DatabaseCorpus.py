from ..DatabaseInterface import DatabaseController as DB

class DatabaseCorpus(object):
    def __init__(self, dictionary):
        self.dictionary = dictionary
        self.DBarticles = DB.articles
    
    def __iter__(self):
        "iterate over the document vectors"
        for doc in self.DBarticles.find():
            yield doc["vector"]

    def fullIter(self): 
        "iterate over the complete database entries"
        return self.DBarticles.find()
    
    def __getitem__(self,key):
        self.getArticle(key)["vector"]

    def getArticle(self,key):
        found = self.DBarticles.find({"_id": key})
        if found.count() < 1: 
            raise Exception("Article ID not found: "+str(key))
        elif found.count() > 1:
            raise Exception("Multiple  articles with ID "+str(key))
        else:
            return found[0]

    def __len__(self):
        return self.DBarticles.count()