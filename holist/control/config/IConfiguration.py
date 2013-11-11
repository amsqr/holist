"""configuration

defines sources, strategies and index/dictionary implementations to use

source -> corpus mapping 1:1 / central corpus or multiples?
"""

def raise_(x):
	raise x

class IConfiguration(object):
	SOURCES = [lambda: raise_(Exception("No sources specified"))]
	STRATEGIES = [lambda: raise_(Exception("No strategies specified"))]
	CORPUS = lambda: raise_(Exception("No corpus implementation specified")) 
	CORPUSSTATIC = None
	PREPROCESSOR  = lambda: raise_(Exception("No preprocessor implementation specified"))
	INDEX = lambda: raise_(Exception("No index implementation specified"))
	DICTIONARY = lambda: raise_(Exception("No dictionary implementation specified"))
