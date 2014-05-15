from holist.util.util import *
ln = getModuleLogger(__name__)

import json

"""
send and receive broadcast messages over the local network.
"""
class Broadcaster(object):
    def __init__(self, sendTag):
        self.sendTag = sendTag

    def broadcast(self, content):
        #TODO look up how to send broadcast packets
        packet = json.dumps({"sender":self.sendTag, "payload":content})
        ln.debug("sending broadcast: %s...", packet[:140])
    #requests.post("whatever the broadcast IP is", BROADCAST_PORT)


class BroadcastListener(object):
    def __init__(self, controller, listenTags):
        self.controller = controller
        self.listenTags = listenTags

    def listen(self):
        # TODO
        pass

    def onReceive(self, message):
        res = json.loads(message)
        tag = res["sender"]
        content = res["payload"]
        if tag in self.listenTags:
            self.controller.notify(tag, content)