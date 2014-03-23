import requests

class Listener(object):
	def __init__(self, ip, port):
		self.ip = ip
		self.port = port

	def notify(self):
		requests.post("http://"+self.ip+str(self.port))
