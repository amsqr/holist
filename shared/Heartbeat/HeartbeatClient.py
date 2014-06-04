__author__ = 'raoulfriedrich'

from core.util.util import *
ln = getModuleLogger(__name__)

import threading, socket, time
from core.model.server.Listener import Listener

BEAT_PERIOD = 5

class HearbeatClient(threading.Thread):

    def __init__(self, listeners):
        super(HearbeatClient, self).__init__()
        self.listeners = listeners

    #def addListener(self, listener):

    def run(self):
        while True:
            hbSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            for listener in self.listeners:
                hbSocket.sendto('PyHB', (listener.ip, int(listener.port)))
                ln.debug("Heartbeat sent to %s:%s", listener.ip, listener.port)

            time.sleep(BEAT_PERIOD)