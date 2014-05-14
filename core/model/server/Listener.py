import requests
from core.util.util import *
ln = getModuleLogger(__name__)

class Listener(object):
	def __init__(self, ip, port):
		self.ip = ip
		self.port = port

	def notify(self, ids=[]):
		try:
			data = {"ids":ids}
			requests.post("http://"+self.ip+":"+str(self.port) + "/notify", data=data)
			ln.debug("notified: %s","http://"+self.ip+":"+str(self.port))
		except Exception, e:
			ln.debug("error occured: %s", str(e))