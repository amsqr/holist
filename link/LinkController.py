__author__ = 'raoulfriedrich'

from core.util.util import *

import logging
import requests
import json

logging.basicConfig(format=config.logFormat,level=logging.DEBUG if config.showDebugLogs else logging.INFO)
ln = getModuleLogger(__name__)

from twisted.internet import reactor
from twisted.internet.task import LoopingCall

class LinkController(object):

    def __init__(self):

        ln.info("Connecting to data collect node.")
        self.connectLoop = None
        self.connectToCore()

        ln.info("running reactor.")
        reactor.run()

    def connectToCore(self):

        def connectUntilDoneIteration():
            ok = self.subscribe()
            if ok:
                self.connectLoop.stop()
                ln.debug("successfully subscribed to core node.")

        self.connectLoop = LoopingCall(connectUntilDoneIteration)
        self.connectLoop.start(5)

    def subscribe(self):
        try:
            ln.info("attempting to subscribe to core node at %s:%s",config.holistcoreurl, config.holistcoreport)

            # my ip and port for callback
            data = {"ip":config.link_node_ip, "port":config.link_node_port}

            # create http post
            res = requests.post("http://"+config.holistcoreurl+":"+str(config.holistcoreport)+"/register_listener", data=data)
            success = json.loads(res.text)["result"] == "success"

            ln.info("successfully subscribed.")
            return success

        except Exception, e:
            ln.warn("couldn't subscribe: %s", str(e))
            return False