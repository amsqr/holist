from util import util
ln = util.getModuleLogger(__name__)
from util import Singleton

from DatabaseCorpus import DatabaseCorpus
from gensim import models, similarities, corpora
from DatabaseInterface import DatabaseController as DB
from DocumentMinimizer import DocumentMinimizer
import smhasher


def hashToken(token):
    return smhasher.murmur3_x86_128(token) % id_range 

class AnalysisController(object):
    __metaclass__ = Singleton.Singleton

    def __init__(self):
        self.corpus = DatabaseCorpus()
        self.dictionary = DatabaseDictionary(createFromDatabase=True)
    
        DocumentMinimizer(self.dictionary)
        
        self.initializeTFIDF()
        self.initializeLSI()
    
    def initializeLSI(self):
        # LSI = models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary)
        self.LSI = models.lsimodel.LsiModel(num_topics=util.LSItopics, corpus=self.corpus, chunksize=1000, id2word=self.dictionary,
            decay=util.LSIdecay, distributed=False, onepass=util.LSIuseOnePass)
    
    def initializeTFIDF(self):
        #TODO: just load a prepared TFIDF from wikipedia
        self.TFIDF = models.tfidfmodel.TfidfModel(self.corpus)
    
    def updateModel(self):
        self.getNewArticles()
        self.preprocessArticles()
        self.updateLSI()
        self.clearNewArticles()
    
    def getNewArticles(self):
        ln.debug("getting new articles from the database")
        self.newArticles = (article for article in DB.newArticles.find())
    
    def preprocessArticles(self):
        ln.debug("minimizing %d articles", len(self.newArticles))
        for article in self.newArticles:
            article["vector"] = DocumentMinimizer().minimize(article["text"])
    
    def updateLSI(self):
        ln.info("updating LSI model")
        newVectors = (a["vector"] for a in self.newArticles) 
        self.LSI.add_documents(newVectors)
    
    def clearNewArticles(self):
        "tell the database to move processed articles out of the processing cue"
        ln.info("clearing new_articles collection")
        for article in self.newArticles:
            DB.handleProcessedArticle(article)

def main():
    updating = True
    while updating:
        runOnce()
if __name__ == "__main__":
    main()