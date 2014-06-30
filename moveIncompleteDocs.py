__author__ = 'dowling'

from backend.core.util.util import *

count = 0
client = getDatabaseConnection()
for article in client.holist.articles.find():

    if not "named_entities" in article["vectors"] or not "LSA" in article["vectors"]:
        count += 1
        client.holist.new_document.insert(article)
        client.holist.articles.remove(article)


print "moved %s articles." % count