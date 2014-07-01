__author__ = 'dowling'
from backend.core.util.util import *
ln = getModuleLogger(__name__)


import json
import datetime
import requests
import numpy as np
from collections import defaultdict
from sklearn.cluster import DBSCAN
from sklearn.cluster import AffinityPropagation

from scipy.spatial.distance import cosine

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


        # retreive similar documents
        matches = self.lshManager.getSimilarDocuments(entityLSA)

        # combine all lsa vectors of the similar documents into a matrix
        lsaMatrix = []
        for match in matches:
            #ln.debug(len(match["lsa"]))
            lsaMatrix.append(np.array(match["lsa"]))

        distanceMatrix = []
        for matchLSA in lsaMatrix:
            row = []
            for otherLSA in lsaMatrix:
                row.append(cosine(matchLSA, otherLSA))
            distanceMatrix.append(row)

        distanceMatrix = np.vstack(distanceMatrix)

        # put the lsa vector matrix into the dbscan clustering algorithm
        #db = DBSCAN(eps=5.0, metric="precomputed", min_samples=1).fit(distanceMatrix)
        af = AffinityPropagation(affinity="precomputed").fit(distanceMatrix)
        cluster_centers_indices = af.cluster_centers_indices_
        labels = af.labels_

        n_clusters_ = len(cluster_centers_indices)

        # cluster labels for each lsa vector
        # labels are numbered from 0 on, -1 is for no cluster / outlier
        #labels = db.labels_
        #ln.debug("Labels: %s", labels)
        #n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0) # number of clusters
        ln.debug('Estimated number of clusters: %d' % n_clusters_)

        clusters = defaultdict(list)
        for x in range(0, len(labels)):
            bucket = labels[x]
            clusters[bucket].append(matches[x])

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