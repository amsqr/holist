angular.
module('App')
    .factory('GraphService', function($http, $controller, AppSettings, d3Service, $log, $window) {

        // var url = "/search_entity?entityName=Brazil";
        // var defaultUrl = "/holist/web/demo.json?entityName=";

        var self = this;
        var graphFactory = $controller(GraphFactory);



        //
        // public interface, inject(scope, element)
        //
        this.inject = function(scope, element, attrs) {
            var initializeGraph = function(d3) {

                var graph = graphFactory.initGraph(d3, element[0]);
                scope.render = graph.render;
                window.onresize = function() {
                    scope.$apply();
                };

                scope.$watch('search', function(newKeyword, oldVals) {
                    return graph.fetchData(newKeyword, graph);
                }, true);

                scope.$watch(function() {
                    return angular.element($window)[0].innerWidth;
                }, function() {
                    graph.render(scope.data);
                });

                graphFactory.onElementsRender = function(parentNode, newResults) {
                     console.log('[onElementsRender] parentNode',parentNode);
                    if (!parentNode.title) return;

                    scope.$parent.activitylog.push({id:parentNode.id, title:parentNode.title, link:parentNode.link });

                }

            }

            d3Service.d3().then(initializeGraph);

        }







        return this;


    })


// usage: <graph></graph>
.directive('graph', function($controller, GraphService) {
    return {
        restrict: 'E',
        scope: {
            search: '='
        },

        template: '<div></div>',
        link: function(scope, element, attrs) {
            GraphService.inject(scope, element, attrs);

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
                $rootScope.$apply(function() {
                    d.resolve(window.d3);
                });
            }
            // Create a script tag with d3 as the source
            // and call our onScriptLoad callback when it
            // has been loaded
            var scriptTag = $document[0].createElement('script');
            scriptTag.type = 'text/javascript';
            scriptTag.async = true;
            scriptTag.src = 'http://d3js.org/d3.v2.js?2.9.1'; //'http://d3js.org/graphService.d3.v3.min.js';
            scriptTag.onreadystatechange = function() {
                if (this.readyState == 'complete') onScriptLoad();
            }
            scriptTag.onload = onScriptLoad;

            var s = $document[0].getElementsByTagName('body')[0];
            s.appendChild(scriptTag);

            return {
                d3: function() {
                    return d.promise;
                }
            };
        }
    ]);
