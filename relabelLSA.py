__author__ = 'dowling'
__author__ = 'dowling'
import requests
from core.util import config
print "requesting LSA relabel of all documents."
r = requests.get("http://localhost:" + str(config.core_control_port) + "/command?command=relabel")
print "got: %s, %s" % (r.status_code, r.text)