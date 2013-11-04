from holist.core.preprocess import IPreprocessor
from stemming.porter2 import stem
import string
import time
from config import config
from util import Singleton
from util import util

# SETTINGS
STOPWORDS = set()


class TokenizingPorter2Stemmer(IPreprocessor):
    __metaclass__ = Singleton

    def __init__(self, dictionary, stopWords=STOPWORDS):
        self.dict = dictionary
        self.stopWords = set(map(stem,stopWords))

    def preprocess(self, doc):
        text = doc.text[:]
        text = text.encode("ascii", "ignore").lower()
        text = removePunctuation(text)
        text = text.split()
        text = stemWords(text)
        text = removeStopWords(set(text))
        text = sorted(text, key=lambda x: -len(x))
        text = getDocumentAsVector(text)
        
        doc.preprocessed = text
    
    def removePunctuation(self,text):
        return text.translate(string.maketrans("",""), string.punctuation)
    
    def removeStopWords(self,textSet):
        return textSet - STOPWORDS
    
    def stemWords(self, text):
        return map(stem, text)
    
    def getDocumentAsVector(self, document):
        """convert the document to bag-of-words representation, 
            and update our dictionary in the process"""
        return self.dict.doc2bow(document, allow_update=True)