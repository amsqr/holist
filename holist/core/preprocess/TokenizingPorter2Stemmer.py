from holist.util.util import *
ln = getModuleLogger(__name__)

from stemming.porter2 import stem
import string
import stopwords

# SETTINGS
STOPWORDS = set(stopwords.stopwords)


class TokenizingPorter2Stemmer():
    def __init__(self, stopWords=STOPWORDS):
        self.stopWords = set(map(stem,stopWords))
        #self.stopWords = set(self.stemWords(self.stopWords))

    def preprocess(self, doc, dictionary):
        if isinstance(doc, str):
            text = doc
        else:
            text = doc.text[:]
        text = text.encode("ascii", "ignore").lower()
        text = self.removePunctuation(text)
        text = text.split()
        text = self.stemWords(text)
        text = self.removeStopWords(set(text))
        text = sorted(text, key=lambda x: -len(x))
        text = dictionary.doc2bow(text, allow_update=True)
        if isinstance(doc, str):
            return text
        else:
            doc.preprocessed = text
    
    def removePunctuation(self,text):
        return text.translate(string.maketrans("",""), string.punctuation)
    
    def removeStopWords(self,textSet):
        return textSet - self.stopWords
    
    def stemWords(self, text):
        return map(stem, text)