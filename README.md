USAGE
====================
To start core and data collection, from top level folder execute:

    # python LSA_startup.py
    # python NER_startup.py
	# python coreStartup.py
	# python collectStartup.py

in separate terminals. (The first two should eventually be merged into a bash script that just starts all available strategies.)

SETUP
===================

install dependencies

    # pip install -r requirements.txt

STRUCTURE / General
====================

The code expects to be able to connect to a MongoDB on port 27017 (default), with a database named "holist". It will use (or automatically create) a "new_documents" collection to store new data, and an "articles" collection to store processed data, meaning articles with their annotated vectors, named entities, etc. It also expects a collection called "rss_feeds", which specifies the URLs of feeds to update. To insert a new source, do e.g.:

	# mongo 
	> use holist
	> db.rss_feeds.insert({"url":"http://feeds.reuters.com/reuters/topNews"})
	>


collectStartup.py starts the data collection node. This currently updates only RSS feeds, but later modules for Twitter, Blogs, etc. will be added in the collect package.

coreStartup.py starts the core analysis node. This node currently performs Latent Semantic Analysis (LSA) and Named Entity Recognition (NER). New strategies (meaning models or algorithms like sentiment analysis) will be added here. The Core will periodically give new documents to these strategies, which then perform their analyses and return vectors (numbers, strings, tuples, whatever) for each document. The Core then adds these vectors to the corresponding document object (i.e. annotates them), and when a document went through all strategies, it is again added to the database, to the "articles" collection. 
The core registers with the collect node, and the collect node sends a notification to the core whenever a new document has been found and added to the "new_documents" collection.




TODO for the backend
====================

We will need to write a node to generate our graphs. This node will register with the core, and the core will notify the node when new documents have been analyzed (meaning annotated). We then retrieve those documents from the "articles" collection, and then, this is the tricky part, use them somehow to generate or update our graphs. 

We might then store these graphs in a new collection ("graphs"). This has the following benefit: We can store this collection externally on a Heroku server. Those can handle more clients easily in comparison to my server, which has processing power but rather slow networking, especially upstream.





DEPENDENCIES
====================
gensim (depends on numpy, scipy)
NLTK (plus the NLTK addtional downloads)
stemming (gonna be removed probably)
twisted
requests
pymongo
feedparser

(This might be incomplete, but you can see pretty quickly if a dependency is missing.)
