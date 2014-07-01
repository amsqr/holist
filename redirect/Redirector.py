__author__ = 'dowling'
from backend.core.util.util import *
logging.basicConfig(format=config.logFormat, level=logging.DEBUG if config.showDebugLogs else logging.INFO)
ln = getModuleLogger(__name__)

from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.resource import Resource

import requests

PORT = 80

ports = {
    "holist": config.link_node_port,
    "user": 49100
}


class Redirect(Resource):
    def getChild(self, path, request):
        pass


class RedirectManager(object):
    def __init__(self):
        root = Redirect()
        factory = Site(root)
        reactor.listenTCP(PORT, factory)
        ln.info("Redirect running.")
        reactor.run()