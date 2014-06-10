angular.
    module('App')
    .controller('HomeController', function($scope,$stateParams,$state, GraphService) {
        console.log('index Controller loaded');

        if ($stateParams.query) {
            $scope.searchKeyword = $stateParams.query;
        }
        //
        // autocompletion with typeahead
        //
        $scope.searchResults = ["LinkedIn","google","Microsoft","Holist","Uber","Sunil Jagani - Person President and Chief Technology Officer @ AllianceTek","Smartface Inc.","Facebook","Vuclip","Roundforest LTD","TransferWise"];


        //
        // perform search
        //
        $scope.onSearch = function() {
            $state.go('search', {query: $scope.searchKeyword});
        }

    });
