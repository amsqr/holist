import gensim
from pymongo import Connection
from ..TopicModeling import DocumentMinimizer
import time

def time_this(func):
    def decorated(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print "Ran in", (time.time() - start), " seconds"
        return result
    return decorated

@time_this
def main():
	conn = Connection("localhost", 27017)
	articles = conn.raw_data.new_articles
	words = conn.analysis.words
	a = loadArticles(articles)
	a = sortArticles(a)
	print len(a)
	minimized = minimizeArticles(a)
	minimized = joinArticles(minimized)
	minSet = toSet(minimized)
	freqs = computeFreqs(minSet, minimized)
	freqs = sortFreqs(freqs)
	printFreqs(freqs)
	return freqs

@time_this
def loadArticles(articleDB):
	print "loadArticles"
	return [article["text"] for article in articleDB.find()]

@time_this
def sortArticles(articles):
	print "sorting"
	return sorted(articles, key=(lambda x: -len(x)))

@time_this
def minimizeArticles(a):
	print "minimizing"
	return [DocumentMinimizer.minimize(doc) for doc in a]

@time_this
def joinArticles(a):
	print "joining"
	return sum(a, [])

@time_this
def toSet(minimized):
	print "creating set"
	return set(minimized)

@time_this
def computeFreqs(minSet, minimized):
	print "computing frequencies"
	return [(term, minimized.count(term)) for term in minSet]

@time_this
def sortFreqs(freqs):
	print "sorting"
	return sorted(freqs,key = (lambda x: x[1]))

@time_this
def printFreqs(freqs):
	for tup in freqs:
		print tup[0], (30-len(tup[0]))*" ", tup[1]