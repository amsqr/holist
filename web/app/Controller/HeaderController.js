angular.
    module('App')
    .controller('HeaderController', function($scope,$rootScope, $location, AuthenticationService) {


        var updateScope = function(event, e){
            console.log('auth status changed',AuthenticationService.user);
            $scope.user = AuthenticationService.user;
            $scope.user_logged_in = AuthenticationService.isLoggedIn();
        };
        $rootScope.$on('user_auth_status_changed', updateScope);
        updateScope();

        $scope.logout = function() {
            $location.url('logout');

        }

    });
