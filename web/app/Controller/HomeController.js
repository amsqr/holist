angular.
module('App')
    .controller('HomeController', function($scope, $stateParams,$log, $http,$state,AppSettings, GraphService) {
        if ($stateParams.query) {
            $scope.searchKeyword = $scope.currentSearch = $stateParams.query;
        } else {
            $scope.currentSearch = 'World Cup';
        }
        //
        // autocompletion with typeahead
        //
        $scope.searchResults = [];
        $scope.activitylog = [];


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
            $('#graphSearch').animate({ top: "-20"}, 1000);

            $state.go('search', {
                query: $scope.searchKeyword
            });
        }
        $scope.updateSearch = function(term) {
            $scope.searchKeyword = term;
        }

        //
        // FAvorites
        //
        $scope.favorites = [];
        var favoritesUrl = AppSettings.apiUrl +  'favorites'
        var getFavorites = function(){

            $http({method: 'GET', url: favoritesUrl}).then(function(results){
                console.log('favorites result', results);
                $scope.favorites = results.data.documents;
            });

        }

        $scope.isFavorite = function(id) {

        }
        $scope.addFavorite = function(documentId) {

            $http.post( favoritesUrl, {document_id: documentId}).then(function(results){
                console.log('save favorite results', results);
                getFavorites();
                // $scope.favorites = results.documents;
            });

        }
        getFavorites();
    });
