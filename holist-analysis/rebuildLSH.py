__author__ = 'dowling'
import requests
from core.util import config
print "requesting LSH index rebuild."
r = requests.get("http://localhost:" + str(config.link_node_control_port) + "/command?command=rebuild")
print "got: %s, %s" % (r.status_code, r.text)