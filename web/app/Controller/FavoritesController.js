angular.
module('App')
    .controller('FavoritesController', function($scope,$controller) {


        var api = $controller(ApiHelper)
        api.setupOverviewPage($scope, 'users/me/favorites');


        api.refresh();

    });
