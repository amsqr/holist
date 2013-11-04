from stemming.porter2 import stem
import string
import time
from config import config
from util import Singleton
from util import util


class DocumentMinimizer(object):
    __metaclass__ = Singleton

    def __init__(self, dictionary, stopWords=util.stopWords):
        self.dict = dictionary
        self.stopWords = set(map(stem,stopWords))

    def minimize(self, doc, numTerms=None):
        document = doc.encode("ascii", "ignore").lower()
        document = removePunctuation(document)
        document = document.split()
        document = stemWords(document)
        document = removeStopWords(document)
        document = sorted(document, key=lambda x: -len(x))
        document = getDocumentAsVector(document)
        if numTerms == None:
            return document
        else:
            return document[:numTerms]
    
    def removePunctuation(self,document):
        return document.translate(string.maketrans("",""), string.punctuation)
    
    def removeStopWords(self,document):
        return [word for word in document if not word in self.stopWords]
    
    def stemWords(self, document):
        return map(stem, document)
    
    def getDocumentAsVector(self, document, allow_update=True):
        """convert the document to bag-of-words representation, 
            and update our dictionary in the process"""
        return self.dict.doc2bow(document, allow_update=allow_update)