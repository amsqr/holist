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
        $scope.searchResults = ["LinkedIn", "google", "Microsoft", "Holist", "Uber", "Sunil Jagani - Person President and Chief Technology Officer @ AllianceTek", "Smartface Inc.", "Facebook", "Vuclip", "Roundforest LTD", "TransferWise"];

        $scope.updateAutocomplete = function(text){
            //if (text.length < 4) return;
            var deferred = $.Deferred();

            var url = AppSettings.apiUrl +  'complete_search?entityName=' + text
            $http({method: 'GET', url: url})
                .success(function(results) {
                    console.log(results);
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
