__author__ = 'dowling'
from core.util.util import *
ln = getModuleLogger(__name__)


import json
import datetime
import requests
from collections import defaultdict


class SimpleClusterStrategy(object):  # just cluster document by date
    def __init__(self, namedEntityIndex, lshManager):
        self.lshManager = lshManager
        self.namedEntityIndex = namedEntityIndex

    def cluster(self, entityName):
        # retrieve the entity in LSA space
        response = requests.get("http://localhost:" + str(config.lsa_strategy_port) + "/small_task", params={"document": entityName})
        if response.status_code != 200:
            return {"result": "False", "reason": "Couldn't run entity search. This is an internal error."}, False

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
            date = datetime.datetime.strptime(document["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
            bucket = str(date.date()) + " " + str(date.hour)
            clusters[bucket].append(document)

        nodes = [{"id": "center", "title": entityName}]
        adj = []
        for idx, (day, cluster) in enumerate(clusters.items()):
            nodes.append(
                {
                    "id": "cluster_" + str(idx),
                    "title": cluster[0]["title"],
                    "documents": dict([("id", d["_id"]) for d in cluster])
                }
            )
            adj.append(("center", "cluster_" + str(idx)))
        ln.debug(nodes)

        return nodes, adj, True