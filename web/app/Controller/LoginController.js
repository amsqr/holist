angular.
module('App')
    .controller('LoginController', function($scope, $stateParams,$location, AuthenticationService, $state) {

        $scope.btnDesc = 'Login';
        $scope.message = null;
        $scope.formDisabled = false;

        //
        // Logout
        //
        if ($location.url() == '/logout') {
            AuthenticationService.logout();
            $scope.message = 'You have been logged out';

        }


        //
        // Login Method
        //
        $scope.login = function() {
            $scope.btnDesc = 'logging in ...';
            $scope.formDisabled = true;


            var request = {
                    email:    $scope.email,
                    password: $scope.password
            };
            console.log('request',request);
            AuthenticationService.signIn(request, function(user){
                $scope.formDisabled = false;
                $scope.btnDesc = 'Login';
                $scope.message = (user?'Successfully logged in':'Error on Login!');

            });
        }


    });
