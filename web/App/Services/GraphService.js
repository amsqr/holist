angular.
    module('App')
    .factory('GraphService', function($http,AppSettings,d3Service,$log,$window) {

        // var url = "/search_entity?entityName=Brazil";
        //var defaultUrl = "/holist/web/demo.json?entityName=";
        var defaultUrl = "http://holist.pcdowling.com/search_entity?entityName=";

        var graphService = this;
        graphService.d3 = null;


// http://blog.thomsonreuters.com/index.php/mobile-patent-suits-graphic-of-the-day/

        this.graph = null;
        var scope;
        var targetElement;

        //
        // public interface, inject(scope, element)
        //
        this.inject = function(_scope, _element, _attrs) {
            scope = _scope;
            targetElement = _element[0];
            d3Service.d3().then(initGraph);

        }

        var initGraph = function( d3 ) {
            graphService.d3 = d3;
            return;

            graphService.graph = myGraph(targetElement);
            scope.render = graphService.graph.render;
            graphService.fetchData('demo',graphService.graph);

            window.onresize = function() {
                scope.$apply();
            };

            scope.$watch(function() {
                return angular.element($window)[0].innerWidth;
            }, function() {
                graphService.graph.render(scope.data);
            });


        }

        this.fetchData = function(keyword, targetGraph) {
            var graphObj = JSON.parse(httpGet(defaultUrl + keyword));
            var vlinks = graphObj.links;
            var vnodes = graphObj.nodes;

            // @todo clear graph?
            for (var i = vnodes.length - 1; i >= 0; i--) {
                targetGraph.addNode(vnodes[i]);
                targetGraph.update();
            }
            for (var i = vlinks.length - 1; i >= 0; i--) {
                targetGraph.addLink(vlinks[i].source.id, vlinks[i].target.id);
            }
        }




        this.initGraph2 = function(d3) {

            graph = new myGraph("#graph");



        }




        function httpGet(theUrl)
        {
            var xmlHttp = null;

            xmlHttp = new XMLHttpRequest();
            xmlHttp.open( "GET", theUrl, false );
            xmlHttp.send( null );
            console.log('HTTP response',xmlHttp.responseText);
            return xmlHttp.responseText;
        }



        function expand(){

            var clickedObject = graphService.d3.select(this).select("id")[0][0]
            if (!clickedObject)
                return $log.error('could not find clicked object',graphService.d3.select(this).select("id"));

            var clickedId = clickedObject.getAttribute("id");

            var clickedNode = nodes[clickedId];
            var docs = clickedNode.documents;
            var argstring = "?";
            docs.forEach(function (doc){
                argstring = argstring + "document=" + doc.id + "&"
            });
            newNodes = JSON.parse(httpGet("/retrieve_documents"+argstring));
        }

        function mouseout() {
            graphService.d3.select(this).select("circle").transition()
                .duration(750)
                .attr("r", 15);
        }
        function mouseover() {
            graphService.d3.select(this).select("circle").transition()
                .duration(750)
                .attr("r", 30);
        }


        function myGraph(el) {
            var self = this;
            var force; // forces
            this.vis; // svg canvas
            var nodes;
            var links;
            var h = 100;
            var w = 100;

            // Add and remove elements on the graph object
            this.addNode = function (node) {
                nodes.push(node);
            }


            var findNode = function (id) {
                for (var i=0; i < nodes.length; i++) {
                    if (nodes[i].id === id)
                        return nodes[i]
                };
            }

            var findNodeIndex = function (id) {
                for (var i=0; i < nodes.length; i++) {
                    if (nodes[i].id === id)
                        return i
                };
            }




            this.removeNode = function (id) {
                var i = 0;
                var n = findNode(id);
                while (i < links.length) {
                    if ((links[i]['source'] === n)||(links[i]['target'] == n))
                        links.splice(i,1);
                    else i++;
                }
                var index = findNodeIndex(id);
                if(index !== undefined) {
                    nodes.splice(index, 1);
                    self.update();
                }
            }

            this.addLink = function (sourceId, targetId) {
                var sourceNode = findNode(sourceId);
                var targetNode = findNode(targetId);

                if((sourceNode !== undefined) && (targetNode !== undefined)) {
                    links.push({"source": sourceNode, "target": targetNode});
                    self.update();
                }
            }





            self.update = function () {

                var link = self.vis.selectAll("line.link")
                    .data(links, function(d) { return d.source.id + "-" + d.target.id; });

                link.enter().insert("line")
                    .attr("class", "link");

                link.exit().remove();

                var node = self.vis.selectAll("g.node")
                    .data(nodes, function(d) { return d.id;});

                var nodeEnter = node.enter().append("g")
                    .attr("class", "node")
                    .call(force.drag);

                nodeEnter.append("circle")
                    .attr("r", 15);

                nodeEnter.append("image")
                    .attr("class", "circle")
                    .attr("x", "-8px")
                    .attr("y", "-8px")
                    .attr("width", "16px")
                    .attr("height", "16px")
                    .on("mouseover", mouseover)
                    .on("click", expand)
                    .on("mouseout", mouseout);

                nodeEnter.append("text")
                    .attr("class", "nodetext")
                    .attr("dx", 12)
                    .attr("dy", ".35em")
                    .text(function(d) {return d.title});

                nodeEnter.append("id").attr("id", function(d) {return d.id;});

                node.exit().remove();

                force.on("tick", function() {
                    link.attr("x1", function(d) { return d.source.x; })
                        .attr("y1", function(d) { return d.source.y; })
                        .attr("x2", function(d) { return d.target.x; })
                        .attr("y2", function(d) { return d.target.y; });

                    node.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
                });

                // Restart the force layout.
                force.start();
            }

            var fullScreenGraph = function() {
                w = jQuery(window).width();
                h = jQuery(window).height() - 60; //for header+ footer
                if (self.vis) {
                    self.vis.attr("width", w)
                        .attr("height", h);

                }

            }
            ///
            //
            self.tick = function () {
                console.log('[GRAPH] tick')

            }
            self.render = function(data) {
                console.log('[GRAPH] render', data);
            }



            // get window dimensions
            fullScreenGraph();

            // init graph
            force = graphService.d3.layout.force()
                .gravity(.05)
                .distance(100)
                .charge(-100)
                .size([w, h]);
            //    .tick(self.tick);

            nodes = force.nodes();
            links = force.links();

            // draw svg
            self.vis = graphService.d3.select(el).append("svg:svg");
           //resize
            fullScreenGraph();



            jQuery( window ).resize(fullScreenGraph);
            // Make it all go
            self.update();

            return this;
        };



        return this;



    })
    // usage: <graph></graph>
    .directive('graph', function($controller,GraphService) {
        return {
            restrict: 'E',
            template: '<div></div>',
            link: function(scope, element, attrs) {
                GraphService.inject(scope,element,attrs);

            },
            controller: function($scope) {


            }
        };
    })
    .factory('d3Service', ['$document', '$q', '$rootScope',
        function($document, $q, $rootScope) {
            var d = $q.defer();
            function onScriptLoad() {
                // Load client in the browser
                $rootScope.$apply(function() { d.resolve(window.d3); });
            }
            // Create a script tag with d3 as the source
            // and call our onScriptLoad callback when it
            // has been loaded
            var scriptTag = $document[0].createElement('script');
            scriptTag.type = 'text/javascript';
            scriptTag.async = true;
            scriptTag.src = 'http://d3js.org/d3.v2.js?2.9.1'; //'http://d3js.org/graphService.d3.v3.min.js';
            scriptTag.onreadystatechange = function () {
                if (this.readyState == 'complete') onScriptLoad();
            }
            scriptTag.onload = onScriptLoad;

            var s = $document[0].getElementsByTagName('body')[0];
            s.appendChild(scriptTag);

            return {
                d3: function() { return d.promise; }
            };
        }]);

