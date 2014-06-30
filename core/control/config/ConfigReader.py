from core.util.util import *
ln = getModuleLogger(__name__)

from core.control.config.IConfiguration import IConfiguration

MANDATORY = ["DATASUPPLY","STRATEGIES","CORPUS","PREPROCESSOR","DICTIONARY","FRONTEND", "LOAD_STRATEGIES"]

def readConfig(filename):
	f = open(filename, "r")
	lines = f.readlines()
	config  = IConfiguration()

	for line in lines:
		line = line.replace(" ","") # strip whitespace

		fieldName = line[:line.find(":")] 
		fieldValue = line[line.find(":")+1:].strip()
		ln.info("%s: %s" % (fieldName, fieldValue))

		if fieldName == "SOURCES":
			sources = fieldValue[1:-1].split(",")
			for source in sources:
				if source == "DummyDataSource":
					from core.datasupply.datasource.DummyDataSource import DummyDataSource
					config.SOURCES.append(DummyDataSource)
				elif source == "Reuters21578DataSource":
					from core.datasupply.datasource.Reuters.Reuters21578DataSource import Reuters21578DataSource
					config.SOURCES.append(Reuters21578DataSource)
				else:
					raise Exception("Unkown data source in config: %s" % (source,))

		elif fieldName == "DATASUPPLY":
			datasupply = fieldValue
			if datasupply == "MongoDataSupply":
				from core.datasupply.DataSupply import MongoDataSupply
				config.DATASUPPLY = MongoDataSupply
			else:
				raise Exception("Unkown data supply wrapper in config: %s" % (datasupply,))
			MANDATORY.remove("DATASUPPLY")

		elif fieldName == "STRATEGIES":
			strategies = fieldValue[1:-1].split(",")
			for strat in strategies:
				if strat == "LSAStrategy":
					from core.model.semantics.LSA.LSAStrategy import LSAStrategy
					config.STRATEGIES.append(LSAStrategy)
				else:
					raise Exception("Unkown strategy in config: %s" % (strat,))
				MANDATORY.remove("STRATEGIES")


		elif fieldName == "CORPUS":
			corpus = fieldValue
			if corpus == "SimpleCorpus":
				from core.model.corpus.simple.SimpleCorpus import SimpleCorpus
				config.CORPUS = SimpleCorpus
			elif corpus == "MongoDBCorpus":
				from core.model.corpus.mongodb.MongoDBCorpus import MongoDBCorpus
				config.CORPUS = MongoDBCorpus
			else:
				raise Exception("Unkown corpus in config: %s" % (corpus,))
			MANDATORY.remove("CORPUS")


		elif fieldName == "PREPROCESSOR":
			preprocessor = fieldValue
			if preprocessor == "TokenizingPorter2Stemmer":
				from core.model.preprocess.TokenizingPorter2Stemmer import TokenizingPorter2Stemmer
				config.PREPROCESSOR = TokenizingPorter2Stemmer
			else:
				raise Exception("Unkown preprocessor in config: %s" % (preprocessor,))
			MANDATORY.remove("PREPROCESSOR")

		elif fieldName == "LOAD_STRATEGIES":
			load = fieldValue
			if load == "True":
				config.LOAD_STRATEGIES = True
			elif load == "False":
				config.LOAD_STRATEGIES = False
			else:
				raise Exception("Unkown LOAD_STRATEGIES value in config: %s", (load,))
			MANDATORY.remove("LOAD_STRATEGIES")


		elif fieldName == "DICTIONARY":
			dictionary = fieldValue
			if dictionary == "SimpleDictionary":
				from core.model.dictionary.simple.SimpleDictionary import SimpleDictionary
				config.DICTIONARY = SimpleDictionary
			elif dictionary == "HashDictionary":
				from core.model.dictionary.hash.HashDictionary import HashDictionary
				config.DICTIONARY = HashDictionary
			else:
				raise Exception("Unkown dictionary in config: %s", (dictionary,))
			MANDATORY.remove("DICTIONARY")


		elif fieldName == "FRONTEND":
			frontend = fieldValue
			if frontend == "HolistFrontend":
				from core.api.TwistedFrontend import HolistFrontend
				config.FRONTEND = HolistFrontend
			elif frontend == "RESTfulFrontend":
				from core.api.RESTfulFrontend import RESTfulFrontend
				config.FRONTEND = RESTfulFrontend
			else:
				raise Exception("Unkown api in config: %s", (frontend,))
			MANDATORY.remove("FRONTEND")
		else:
			raise Exception("Invalid category in %s: %s" % (filename, fieldName))

	if MANDATORY:
		raise Exception("Missing categories: %s", MANDATORY)
	return config











