angular.
module('App')
    .controller('HomeController', function($scope, $stateParams,$log, $http,$state,AppSettings, GraphService) {
        if ($stateParams.query) {
            $scope.searchKeyword = $scope.currentSearch = $stateParams.query;
        } else {
            $scope.currentSearch = 'demo';
        }
        //
        // autocompletion with typeahead
        //
        $scope.searchResults = [];



        $scope.updateAutocomplete = function(){
            //if (text.length < 4) return;
            var deferred = $.Deferred();
            if (!$scope.searchKeyword)
                return deferred.reject();

            var url = AppSettings.apiUrl +  'complete_search?entityName=' + $scope.searchKeyword
            $http({method: 'GET', url: url})
                .success(function(results) {
                    if (!results) { return deferred.reject(); }
                    $scope.searchResults = results;
                    deferred.resolve($scope.searchResults);
                })
                .error(function(data, status, headers, config) {
                    $log.error('error on fetching autocomplete', url);
                });
            return deferred.promise();
        };

        //
        // perform search
        //
        $scope.onSearch = function() {
            $state.go('search', {
                query: $scope.searchKeyword
            });
        }
    });
