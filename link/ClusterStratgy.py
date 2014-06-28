__author__ = 'dowling'
from core.util.util import *
ln = getModuleLogger(__name__)


import json
import datetime
import requests
from collections import defaultdict
from sklearn.cluster import DBSCAN

from dateutil import parser


class SimpleClusterStrategy(object):  # just cluster document by date
    def __init__(self, namedEntityIndex, lshManager):
        self.lshManager = lshManager
        self.namedEntityIndex = namedEntityIndex

    def cluster(self, entityName):
        # retrieve the entity in LSA space
        response = requests.get("http://localhost:" + str(config.lsa_strategy_port) + "/small_task", params={"document": entityName})
        if response.status_code != 200:
            return {"result": "False", "reason": "Couldn't run entity search. This is an internal error."}, [], False

        entityLSA = None
        responseJSON = json.loads(response.text)
        ln.debug(responseJSON)
        for vector in responseJSON["vectors"]:
            if vector["strategy"].startswith("LSA"):
                entityLSA = vector["vector"]
                break

        matches = self.lshManager.getSimilarDocuments(entityLSA)

        clusters = defaultdict(list)
        for document in matches:
            try:
                date = datetime.datetime.strptime(document["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                date = parser.parse(document["timestamp"])
            hour = (date.hour if date.hour % 2 == 1 else date.hour - 1)
            bucket = str(date.date()) + " " + str(hour)
            clusters[bucket].append(document)

        nodes = [{"id": "center", "name": "center", "title": entityName}]
        adj = []
        for idx, (day, cluster) in enumerate(clusters.items()):
            node = {
                "id": "cluster_" + str(idx),
                "name": "cluster_" + str(idx),
                "title": cluster[0]["title"],
                "documents": [{"id": d["_id"], "title": d["title"]} for d in cluster],
                "weight": len(cluster)
            }
            nodes.append(node)
            #adj.append({"source": 0, "target": idx + 1, "value": "1"})
            adj.append({"source": nodes[0], "target": node, "value": "1"})
            #adj.append({"source": "center", "sourceTitle": entityName,
            #            "target": "cluster_" + str(idx), "targetTitle": cluster[0]["title"],
            #            "value": "1"})
        ln.debug(nodes)

        return nodes, adj, True

class DBSCANClusterStrategy(object):
    def __init__(self, namedEntityIndex, lshManager):
        self.lshManager = lshManager
        self.namedEntityIndex = namedEntityIndex

    def cluster(self, entityName):
           # retrieve the entity in LSA space
        response = requests.get("http://localhost:" + str(config.lsa_strategy_port) + "/small_task", params={"document": entityName})
        if response.status_code != 200:
            return {"result": "False", "reason": "Couldn't run entity search. This is an internal error."}, [], False

        entityLSA = None
        responseJSON = json.loads(response.text)
        ln.debug(responseJSON)
        for vector in responseJSON["vectors"]:
            if vector["strategy"].startswith("LSA"):
                entityLSA = vector["vector"]
                break

        matches = self.lshManager.getSimilarDocuments(entityLSA)

        X = []
        #for match in matches:
         #   X.append(match.vectors["LSA"])

        #ln.debug(X)
        #db = DBSCAN(eps=0.3, min_samples=1).fit(X)
        #core_samples = db.core_sample_indices_
        #labels = db.labels_

        clusters = defaultdict(list)
        for document in matches:
            try:
                date = datetime.datetime.strptime(document["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                date = parser.parse(document["timestamp"])
            hour = (date.hour if date.hour % 2 == 1 else date.hour - 1)
            bucket = str(date.date()) + " " + str(hour)
            clusters[bucket].append(document)

        nodes = [{"id": "center", "name": "center", "title": entityName}]
        adj = []
        for idx, (day, cluster) in enumerate(clusters.items()):
            node = {
                "id": "cluster_" + str(idx),
                "name": "cluster_" + str(idx),
                "title": cluster[0]["title"],
                "documents": [{"id": d["id"], "title": d["title"]} for d in cluster],
                "weight": len(cluster)
            }
            nodes.append(node)
            #adj.append({"source": 0, "target": idx + 1, "value": "1"})
            adj.append({"source": nodes[0], "target": node, "value": "1"})
            #adj.append({"source": "center", "sourceTitle": entityName,
            #            "target": "cluster_" + str(idx), "targetTitle": cluster[0]["title"],
            #            "value": "1"})
        ln.debug(nodes)

        return nodes, adj, True