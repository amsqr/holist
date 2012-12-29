import logging
logging.basicConfig(format='%(asctime)s :    %(message)s', level=logging.INFO)

from DatabaseDictionary import DatabaseDictionary
from DatabaseCorpus import DatabaseCorpus
from gensim import models, similarities
from ..DatabaseInterface import DatabaseController as DB
import DocumentMinimizer
import time

#update intervall in seconds
updateEvery = 120

dictionary = None
corpus = None
LSIdecay = 0.95

TFIDF = None
LSI = None

newArticles = None

def init():
    global dictionary, corpus
    DocumentMinimizer.init()
    
    dictionary = DatabaseDictionary()
    corpus = DatabaseCorpus(dictionary)
    initializeTFIDF()
    initializeLSI()

def initializeLSI():
    global LSI, corpus, dictionary, LSIdecay
    LSI = models.lsimodel.LsiModel(corpus=corpus, id2word=dictionary, chunksize=1000, 
        decay=LSIdecay, distributed=False, onepass=True)

def initializeTFIDF():
    global TFIDF, corpus
    TFIDF = models.tfidfmodel.TfidfModel(corpus)

def updateTFIDF():
    global newArticles, TFIDF
    logging.info("updating TFIDF model")
    newVectors = (a["vector"] for a in newArticles)
    TFIDF.add_documents(newVectors)

def updateLSI():
    global newArticles, TFIDF, LSI
    logging.info("updating LSI model")
    newVectors = (a["vector"] for a in newArticles)
    LSI.add_documents(newVectors)

def preprocessArticles():
    global newArticles
    logging.info("minimizing %d articles", len(newArticles))
    for i, article in enumerate(newArticles):
        if(i%1000==0):
            print i
        article["vector"] = DocumentMinimizer.minimize(article["text"])

def getNewArticles():
    global newArticles
    logging.info("getting new articles from the database")
    newArticles = list(DB.newArticles.find())

def clearNewArticles():
    global newArticles
    "tell the database to move processed articles out of the processing cue"
    logging.info("clearing new_articles collection")
    for article in newArticles:
        DB.handleProcessedArticle(article)

def updateModel():
    getNewArticles()
    preprocessArticles()
    updateTFIDF()
    updateLSI()
    clearNewArticles()

def runOnce():
    updateModel()

def main():
    global updateEvery
    updating = True
    while updating:
        iterStart = time.time()

        runOnce()

        sleepTime = updateEvery - (time.time() - iterStart)
        if sleepTime > 0:
            time.sleep(sleepTime)

if __name__ == "__main__":
    main()