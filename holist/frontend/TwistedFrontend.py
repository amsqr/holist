from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.internet import reactor
import cgi
import json

class HolistFrontend(object):
    def __init__(self, controller):
        self.controller = controller
        self.setupResources()

    def setupResources(self):
        root = Resource()
    
        queryTextPage = QueryText(self.controller)
        queryIdPage = QueryId(self.controller)
        displayArticlePage = DisplayArticle(self.controller)
        mainPage = MainPage()
        
        root.putChild("query_text", queryTextPage)
        root.putChild("query_id", queryTextPage)
        root.putChild("render_article", displayArticlePage)
        root.putChild("", mainPage)
        factory = Site(root)
        reactor.listenTCP(8080, factory)
		

class MainPage(Resource):
    def render_GET(self, request):
        return """
        <html>
        	<form name="input" action="query_text" method="post">
				Enter query text: <input type="text" name="query">
				<input type="submit" value="Submit">
			</form>
		</html>
        """

class QueryText(Resource):
    def __init__(self, controller):
        self.controller = controller

    def render_POST(self, request):
        queryText = cgi.escape(request.args["query"][0])
        queryResults = self.controller.queryText(queryText)
        resultTables = ""

        for strat in self.controller.strategies:
            resultAsTable = """<br/>%s<br/><table border="1">""" % strat.NAME
            for res in queryResults[strat.NAME]:
            	resultAsTable += """<tr><td><a href="/render_article?id=%s">%s</a></td><td>%s</td></tr>""" % (res[0],res[0], res[1],)
            resultAsTable += """</table>"""
            resultTables += resultAsTable
       	html = """
       	<html>
       		<head>%s</head><br/>
       		<body>
			%s
       		</body>
		</html>
       	""" % (queryText,resultTables)
        return html

class QueryId(Resource):
    def __init__(self, controller):
        self.controller = controller

    def render_GET(self, request):
        res = int(self.controller.queryId(request.args["id"][0]))
        return """"<html>
       		<head>%s</head><br/>
       		<body>
			%s
       		</body>
		</html>""" & (request.args["id"][0], res,)

class DisplayArticle(Resource):
    def __init__(self, controller):
        self.controller = controller

    def render_GET(self, request):
        id = int(request.args["id"][0])
        doc = self.controller.corpus[id]
        return """<html>
       		<head>%s</head><br/>
       		<body>
			%s
       		</body>
		</html>""" % (str(doc.id), doc.text,)