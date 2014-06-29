angular.
module('App')
    .controller('FavoritesController', function($scope) {

        var api = $controller(ApiHelper)
        api.setupOverviewPage($scope, 'favorites');
        api.refresh();

    });
