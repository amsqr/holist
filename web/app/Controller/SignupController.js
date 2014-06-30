angular.
    module('App')
    .controller('SignupController', function($scope, $stateParams,$location, AuthenticationService, $state) {
        //reqistrationForm

        $scope.btnDesc = 'Register';
        $scope.message = null;
        $scope.user = {};
        $scope.formDisabled = false;


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
                    $scope.message = err;
                    return;
                }
                $scope.message = ('Your account has been created.');

                if (user) // successful login
                    $scope.showLoginForm = false;

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


