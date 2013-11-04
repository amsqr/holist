import logging
logging.basicConfig(format='%(asctime)s :    %(message)s', level=logging.INFO)

from xml.dom.minidom import *
from holist.SourceScraper import RuleManager
from holist.TopicModeling import DocumentMinimizer as dm
from gensim import corpora, models, similarities
import ast

articles = []
dictionary = None
corpus = None
hdp = None
lda = None
index  = None
tfidf = None
def readFiles(files=22):
    global articles
    documentFiles = ["reuters21578/reut2-0"+(("00"+str(n))[-2:])+".xml" for n in range(files)]
    rule = RuleManager.getRule("21578","")
    for idx,f in enumerate(documentFiles):
        print idx, f
        fi = open(f,"r")
        for (title, date, text) in rule(str(idx),fi.read()):
            articles.append({"title":title, "date":date, "text":text, "vector":""})
            #print len(title)
        fi.close()
    

def minimizeArticles():
    global articles
    logging.info(str(len(articles))+ " articles parsed. Minimizing...")
    
    for i,article in enumerate(articles):
        article["vector"] = dm.minimize(article["text"],None) #Note: vector isn't a vector yet here.
        if(i%1000==0):
            logging.info( "..."+str(i))
    logging.info("writing minimized corpus to file")
    out = open("tmp/reuters21578.txt","w")
    out.write(str(articles))
    out.close()

def createDictionary(filt=True, no_below=5, no_above=0.5):
    global articles, dictionary
    logging.info("creating dictionary...")
    dictionary = corpora.Dictionary([article["vector"] for article in articles]) #Note: vector isn't a vector yet here.
    if filt:
        logging.info("Filtering extremely common/uncommon words")
        dictionary.filter_extremes(no_below=no_below, no_above=no_above, keep_n=None)
    logging.info( "Saving dictionary")
    dictionary.save('tmp/ReutersTest.dict')

def createCorpus():
    global articles, corpus
    logging.info( "Creating vectorized corpus...")
    for a in articles:
        a["vector"] = dictionary.doc2bow(a["vector"])
    corpus = ReutersCorpus(articles, dictionary)
    corpora.MmCorpus.serialize('tmp/ReutersTest.mm', corpus)

def initialize(reload=False,files=22, filt=True, no_below=5, no_above=0.5):
    if reload:
        readFiles(files)
        minimizeArticles()
    else:
        loadRaw()
    createDictionary(filt, no_below, no_above)
    createCorpus()

def loadRaw():
    global articles
    inp = open("tmp/reuters21578.txt","r")
    articles = ast.literal_eval(inp.read())
    inp.close()

def load():
    global dictionary, corpus
    articles = json.load("tmp/reuters21578.json")
    dictionary = corpora.Dictionary.load('tmp/ReutersTest.dict')
    corpus = corpora.MmCorpus('tmp/ReutersTest.mm')

def createHDP(kappa=1,K=15,T=300,tau=64.0,alpha=1, gamma=1, eta=1.5, scale=1.0, var_converge=0.0001):
    """
    T = Top level truncation for HDP
    K = Second level truncation for HDP

    gamma: first level concentration 
    alpha: second level concentration 
    eta: the topic Dirichlet -> this varies directly with the density of the topics and inversely with the number of topics found
    T: top level truncation level -> effectively max number of topics
    K: second level truncation level 
    kappa: learning rate. larger corpus -> smaller kappa
    tau: slow down parameter
    """
    global dictionary, corpus, hdp
    logging.info( "creating HDP model for corpus...")
    hdp = models.hdpmodel.HdpModel(corpus=corpus, id2word=dictionary, kappa=kappa,tau=64.0, K=K, T=T, alpha=alpha, gamma=gamma, eta=eta, scale=scale,var_converge=var_converge)
    logging.info("Saving model.")
    hdp.save('tmp/ReutersHDP.hdp')


def applyTFIDF():
    global corpus, tfidf, dictionary
    logging.info("Creating and applying TF-IDF model to corpus...")
    tfidf = models.tfidfmodel.TfidfModel(corpus)
    for idx,doc in enumerate(corpus): 
        docTFIDF=tfidf[doc]
        for i,term in enumerate(doc):
            corpus.articles[idx]["vector"][i] = (term[0],term[1] * docTFIDF[i][1])
    corpora.MmCorpus.serialize('tmp/ReutersTestTFIDF.mm', corpus)



def loadHDP():
    global hdp
    hdp = models.hdpmodel.HdpModel.load('tmp/ReutersHDP.hdp')

def loadAll():
    global dictionary, corpus, hdp, lda, index
    dictionary = corpora.Dictionary.load('tmp/ReutersTest.dict')
    corpus = corpora.MmCorpus('tmp/ReutersTest.mm')
    
    hdp = models.hdpmodel.HdpModel.load('tmp/ReutersHDP.hdp')
    lda = models.ldamodel.LdaModel.load('tmp/ReutersLDAfromHDP.lda')
    index = similarities.docsim.MatrixSimilarity.load('tmp/ReutersHDPtoLDA.index')

def saveAll():
    global dictionary, corpus, hdp, lda, index
    dictionary.save('tmp/ReutersTest.dict')
    corpora.MmCorpus.serialize('tmp/ReutersTest.mm', corpus)
    
    hdp.save('tmp/ReutersHDP.hdp')
    lda.save('tmp/ReutersLDAfromHDP.lda')
    index.save('tmp/ReutersHDPtoLDA.index')

def runQuery(q, minimize=True):
    global index, lda, dictionary, corpus
    if minimize:
        q = dm.minimize(q,None)
        if q== "":
            logging.warning("running empty query (after minimizations)")
    else:
        q = q.split()
    vec_lda = lda[dictionary.doc2bow(q)]
    sims = sorted(enumerate(index[vec_lda]),key=lambda x: -x[1])
    def toNormal(articleID):
        return corpus.getArticle(articleID[0])
    return (toNormal(a) for a in sims)

def createLDA():
    global hdp, lda
    logging.info("Creating equivalent LDA Model for transformations.")
    (alpha,beta) = hdp.hdp_to_lda()
    lda = models.LdaModel(id2word=hdp.id2word,num_topics=len(alpha), alpha=alpha,eta=hdp.m_eta)
    lda.save('tmp/ReutersLDAfromHDP.lda')

def createIndex():
    global lda, corpus, index
    index = similarities.MatrixSimilarity(lda[corpus])
    index.save('tmp/ReutersHDPtoLDA.index')

def main():
    initialize()
    createHDP()
    createLDA()
    createIndex()

class ReutersCorpus(object):
    def __init__(self, articles, dictionary):
        self.articles = articles
        self.dictionary = dictionary
    
    def __iter__(self):
        for doc in self.articles:
            yield doc["vector"]
    
    def __getitem__(self,key):
        return self.articles[key]["vector"]

    def getArticle(self,key):
        return self.articles[key]

    def __len__(self):
        return len(self.articles)

if __name__ == "__main__":
    main()