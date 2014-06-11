angular.
module('App')
    .controller('HomeController', function($scope, $stateParams, $state, GraphService) {
        if ($stateParams.query) {
            $scope.searchKeyword = $scope.currentSearch = $stateParams.query;
        } else {
            $scope.currentSearch = 'demo';
        }
        //
        // autocompletion with typeahead
        //
        $scope.searchResults = ["LinkedIn", "google", "Microsoft", "Holist", "Uber", "Sunil Jagani - Person President and Chief Technology Officer @ AllianceTek", "Smartface Inc.", "Facebook", "Vuclip", "Roundforest LTD", "TransferWise"];


        //
        // perform search
        //
        $scope.onSearch = function() {
            $state.go('search', {
                query: $scope.searchKeyword
            });
        }
    });
