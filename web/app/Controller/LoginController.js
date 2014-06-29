angular.
module('App')
    .controller('LoginController', function($scope, $stateParams,$location, AuthenticationService, $state) {

        $scope.btnDesc = 'Login';
        $scope.message = null;
        $scope.formDisabled = false;
        $scope.showLoginForm = true;

        //
        // Logout
        //
        if ($location.url() == '/logout') {
            AuthenticationService.logout();
            $scope.message = 'You have been logged out';
            $scope.showLoginForm = true;

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
            AuthenticationService.signIn(request, function(err, user){

                $scope.formDisabled = false;

                $scope.btnDesc = 'Login';

                if (err){
                    switch (err){
                        case 'not_found':
                            $scope.message = 'The given user could not be found';
                            break;

                        case 'bad_request':
                            $scope.message = 'The given request was not complete';
                            break;
                        default:
                            $scope.message = 'An unkown error occured:' + err;
                    }
                    return;
                }

                $scope.message = ('Successfully logged in');

                if (user) // successful login
                    $scope.showLoginForm = false;

            });
        }


    });
