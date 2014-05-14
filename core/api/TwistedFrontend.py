from core.util.util import *
ln = getModuleLogger(__name__)

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
        mainPage = MainPage(self.controller)
        
        root.putChild("query_text", queryTextPage)
        root.putChild("query_id", queryIdPage)
        root.putChild("render_article", displayArticlePage)
        root.putChild("", mainPage)
        factory = Site(root)
        reactor.listenTCP(8080, factory)
        

class MainPage(Resource):
    def __init__(self, controller):
        self.controller = controller

    def render_GET(self, request):#<input type="submit" value="Submit">
    #vertical-align:middle;width:350px;margin:0 auto;
        return """
        <html>
            <body bgcolor="#DBDBDB">
                <div style="
                        height:150px;
                        position:absolute;
                        left:50%;
                        top:60%;
                        margin:-75px 0 0 -135px;">
                    <form name="input" action="query_text" method="post"> 
                        <input type="border:0;text" name="query" style="height:30px;width:300px;margin:0 auto;">
                    </form>
                </div>
            </body>
        </html>
        """ #<div> %s</div>% (str(self.controller.strategies[0].getOverview()),)

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
                resultAsTable += """<tr>
                                        <td><a href="/query_id?id=%s">%s</a>
                                            <a href="/render_article?id=%s"> (Text)</a>
                                        </td>
                                        <td>%s</td>
                                        <td>%s</td>
                                    </tr>""" % (res[0],res[0],res[0], res[1],str(self.controller.corpus[res[0]].text))
            resultAsTable += """</table>"""
            resultTables += resultAsTable
        html = """
        <html>
            <head>Query: "%s"</head><br/>
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
        queryId = int(request.args["id"][0])
        queryResults = self.controller.queryId(queryId)
        resultTables = ""

        for strat in self.controller.strategies:
            resultAsTable = """<br/>%s<br/><table border="1">""" % strat.NAME
            for res in queryResults[strat.NAME]:
                resultAsTable += """<tr><td><a href="/query_id?id=%s">%s</a>
                                            <a href="/render_article?id=%s"> (Text)</a>
                                            </td><td>%s</td><td>%s</td></tr>""" % (res[0],res[0],res[0], res[1],str(self.controller.corpus[res[0]].text))
            resultAsTable += """</table>"""
            resultTables += resultAsTable
        html = """
        <html>
            <head>Document: %s<br/>%s<br/></head><br/>
            <body>
            %s
            </body>
        </html>
        """ % (queryId, str(self.controller.corpus[queryId].text) ,resultTables)
        return html

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
        </html>""" % (str(doc.id), str(doc.text),)