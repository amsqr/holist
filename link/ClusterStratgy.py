__author__ = 'dowling'
from core.util.util import *
ln = getModuleLogger(__name__)


import json
import datetime
import requests
from collections import defaultdict


class SimpleClusterStrategy(object):  # just cluster document by date
    def cluster(self, entityName):
        # retrieve the entity in LSA space
        response = requests.get("http://localhost:" + config.lsa_strategy_port + "/small_task", params={"text": entityName})
        if response.stats_code != 200:
            return {"result": "False", "reason": "Couldn't run entity search. This is an internal error."}, False

        entityLSA = None
        for vector in json.loads(response.text)["vectors"]:
            if vector["strategy"] == "LSA":
                entityLSA = vector["vector"]
                break

        matches = self.lshManager.getSimilarDocuments(entityLSA)
        clusters = defaultdict(list)
        for document in matches:
            day = datetime.datetime.strptime(document["timestamp"], "%Y-%m-%d").date()
            clusters[day].append(document)

        nodes = [{"id": "center", "title": entityName}]
        for idx, (day, cluster) in enumerate(clusters.items()):
            nodes.append(
                {
                    "id": "cluster_" + str(idx),
                    "title": cluster[0]["title"],
                    "documents": dict([("id", d["_id"]) for d in cluster])
                }
            )

        return nodes, True