__author__ = 'dowling'

import pymongo

from core.util.util import *

count = 0
client = getDatabaseConnection()
for article in client.holist.articles.find():
    print article["vectors"]
    break

    if not "NamedEntities" in article["vectors"] or not "LSA" in article["vectors"]:
        count += 1

print count