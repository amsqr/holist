angular.
module('App')
    .controller('HomeController', function($scope,$controller, $stateParams,$log, $http,$state,AppSettings, GraphService) {
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
        //local methods
        $scope.favorites = [];
        var favoritesUrl = AppSettings.apiUrl +  'favorites'
        var getFavorites = function(){

            $http({method: 'GET', url: favoritesUrl}).then(function(results){
                console.log('favorites result', results);
                $scope.favorites = results.data.documents;
            });

        }

        $scope.isFavorite = function(id) {
            for (i in $scope.favorites){
                if ($scope.favorites[i]._id == id){
                    return true;
                }
            }
            return false;
        }

        //
        // Api Interface
        //

        // @todo: only if authenticated..
        var favoritesApi = $controller(ApiHelper);
        favoritesApi.setupOverviewPage($scope, 'users/me/favorites','favorites');


        $scope.addFavorite = function(documentId) {
            favoritesApi.doHttpRequest({
                method:"POST",
                data: {url: 'users/me/favorite', document_id: documentId}

            },function() {
                console.log('favorites added');
            })
        }
        favoritesApi.refresh();
        // getFavorites();
    });
