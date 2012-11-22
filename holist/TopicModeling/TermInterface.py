from Term import Term
from ..DatabaseInterface import DatabaseController

words = None
terms = None
def init(): #called on start. get all known terms into memory
	global terms, words
	termsRaw = DatabaseController.getWords()
	words = set([t["sid"] for t in termsRaw]) #for quickly checking whether a term is known.
	terms = [Term(t["_id"], t["sid"], t["occurrences"]) for t in termsRaw] #the actual term objects, slower but also hold more data.


def handleDocument(document):
	"""take a document, extract all terms from it, update the term mapping and update the database."""
	#TODO: Word mapping
	global terms, words
	for word in document:
		if word in words:
			term = findTerm(word) #we already know this word, lets find the term
			term.occurrences += 1
		else:
			term = Term(0, word, 1) #create a new Term. ID will be set once the term is added to the database
			terms.append(term)
			words.add(word)
		DatabaseController.addWord(term) # this handles IDs and updated automatically. if the word was previously in the database, it will simply update.
	terms.sort(key = lambda x: x.occurrences) #keep the list of terms sorted.

def findTerm(word):
	for term in terms:
		if term.sid == word:
			return term
