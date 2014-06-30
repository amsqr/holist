angular.
    module('App')
    .controller('SignupController', function($scope, $stateParams,$location, AuthenticationService, $state) {
        //reqistrationForm

        $scope.btnDesc = 'Register';
        $scope.message = null;
        $scope.user = {};
        $scope.formDisabled = false;
        $scope.showForm = true;

        //
        // Registration Method
        //
        $scope.register = function() {
            $scope.btnDesc = 'creating account ...';
            $scope.formDisabled = true;

            AuthenticationService.signUp($scope.user, function(err, user){
                $scope.formDisabled = false;
                $scope.btnDesc = 'Register';

                if (err) {
                    console.log('signup error', err, user);
                    if (err == 'Conflict') {
                        $scope.message = 'This user exists already.';
                    } else {
                        $scope.message = err;
                    }
                    return;
                }
                $scope.message = ('Your account has been created. And you have been logged in successfully.');
                if (user) // successful login
                    $scope.showForm = false;

            });
        }


    })
    .directive("repeatPassword", function() {
        return {
            require: "ngModel",
            link: function(scope, elem, attrs, ctrl) {
                var otherInput = elem.inheritedData("$formController")[attrs.repeatPassword];

                ctrl.$parsers.push(function(value) {
                    if(value === otherInput.$viewValue) {
                        ctrl.$setValidity("repeat", true);
                        return value;
                    }
                    ctrl.$setValidity("repeat", false);
                });

                otherInput.$parsers.push(function(value) {
                    ctrl.$setValidity("repeat", value === ctrl.$viewValue);
                    return value;
                });
            }
        };
    });


