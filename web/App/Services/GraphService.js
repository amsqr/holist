
angular.
    module('App')
        .factory('GraphService', function($http,$q,AppSettings,d3Service,$log,$window) {

        // var url = "/search_entity?entityName=Brazil";
       // var defaultUrl = "/holist/web/demo.json?entityName=";
        var defaultUrl = "http://holist.pcdowling.com/search_entity?entityName=";

        var self = this;



        //
        // public interface, inject(scope, element)
        //
        this.inject = function(scope, element, attrs) {
            var initializeGraph = function(d3) {

                var graph = Graph(d3, element[0]);
                scope.render = graph.render;
                window.onresize = function() {
                    scope.$apply();
                };
                scope.$watch('search', function(newKeyword, oldVals) {
                    return self.fetchData(newKeyword, graph);
                }, true);

                scope.$watch(function() {
                    return angular.element($window)[0].innerWidth;
                }, function() {
                    graph.render(scope.data);
                });

            }

            d3Service.d3().then(initializeGraph);

        }


        this.fetchData = function(keyword, targetGraph) {

            console.log('[graph] fetching keyword',keyword);
            httpGet(defaultUrl + keyword)
                .then(function(graphObj,status){
                    var vlinks = graphObj.links;
                    var vnodes = graphObj.nodes;

                    targetGraph.clearNodes();

                    for (var i = vnodes.length - 1; i >= 0; i--) {
                        targetGraph.addNode(vnodes[i]);

                    }
                    for (var i = vlinks.length - 1; i >= 0; i--) {
                        targetGraph.addLink(vlinks[i].source.id, vlinks[i].target.id);
                    }
                    targetGraph.update();

                });


        }




        function httpGet(requestUrl)
        {
            var d = $q.defer();
            $http({method: 'GET', url:requestUrl })
                .success(function(data, status, headers, config) {
                    console.log('[GRAPH] Get Data successful',data,status);
                    d.resolve(data,status);
                })
                .error(function(data, status, headers, config) {
                    d.reject(data,status);
                });

            return d.promise;

            /*    var xmlHttp = null;

            xmlHttp = new XMLHttpRequest();
            xmlHttp.open( "GET", theUrl, false );
            xmlHttp.send( null );
            return xmlHttp.responseText;*/
        }

        return this;


    })


    // usage: <graph></graph>
    .directive('graph', function($controller,GraphService) {
        return {
            restrict: 'E',
            scope: {
                search: '='
            },

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

