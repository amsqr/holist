USAGE
====================
To start core and data collection, from top level folder execute:

    # python LSA_startup.py
    # python NER_startup.py
	# python coreStartup.py
	# python collectStartup.py
	# sudo python linkStartup.py

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

coreStartup.py starts the core annotation node. This node currently performs Latent Semantic Analysis (LSA) and Named Entity Recognition (NER), and saves this information. New strategies (models or algorithms like LDA, sentiment analysis, other classification) can be added here. The Core will periodically give new documents to these strategies, which then perform their analyses and return vectors (numbers, strings, tuples, whatever) for each document. The Core then adds these vectors to the corresponding document object (i.e. annotates them), and when a document went through all strategies, it is again added to the database, to the "articles" collection. 
The core registers with the collect node, and the collect node sends a notification to the core whenever a new document has been found and added to the "new_documents" collection.

The link package represents the layer the performs analysis and orgaization on the documents that have been annotated by the core. Currently, this means building an LSH index for all LSA annotated documents, and clustering similar articles. Later on, this is where different views and organizations such as timelines or map views, as well as advanced analytics such as relationships between entities can be implemented.


