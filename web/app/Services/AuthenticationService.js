'use strict';

angular.module('App')
    .service('AuthenticationService', function ($rootScope, $location,$http,$log,AppSettings) {


        this.user = null;
        this.token = null;
        var self = this;
        var mockServer = true;


        var redirect_login_page = function() {
            $location.path('/login/');
            $rootScope.$apply();
        }

        this.init = function() {

            var token = localStorage.getItem('accessToken');
            if (token == 'null') {
                token = null;
            }
            this.updateToken(token);
            if ($location.path().indexOf('/login') == -1) { //do not redirect on login
                window.setTimeout(function() { self.ensureAuthentication(); }, 1500);
            }
        };

        this.logout = function () {
            this.updateToken(null);
            this.user = null;
            $rootScope.$broadcast('user_auth_status_changed');
            notifyObservers();

        };

        this.updateToken = function(token) {
            if (!token){
                delete $http.defaults.headers.common['X-Token'];
                delete $http.defaults.headers.common['access_token'];
                localStorage.removeItem('userToken');
                this.token = null;
                return;
            }
            this.token = token;
            $http.defaults.headers.common['X-Token'] = token;
            $http.defaults.headers.common['access_token'] = token;
            localStorage.setItem('accessToken', token);
        }

        /**
         * Get user data
         */
        this.fetchCurrentUser = function() {
            UserFactory.getMe()
                .success(function(response) {

                    var data = response.data
                    self.user = data;

                    $rootScope.$broadcast('user_auth_status_changed');
                    notifyObservers();

                }).error(function(response) {
                    self.logout();
                    redirect_login_page();
                });

        }
        this.getUser = function() {
            return this.user;
        }
        this.isLoggedIn = function() {
            return (this.token != null);
        };
        this.ensureAuthentication = function() {

            if (this.isLoggedIn()) {
                this.fetchCurrentUser();
            }   else {
                redirect_login_page();
            }

        }

        this.requestPassword = function(callback, email) {

            $http({
                method: "POST",
                url: AppSettings.serverURI + '/user/reset_password',
                data: {email:email}
            }).success(function(data) {
                    callback(data);
                });


        }
        this.signUp = function(user, callback) {

            $http({
                method: "POST",
                url: AppSettings.serverURI + '/user/signUp',
                data: {'username':user.username,
                    'password':user.password,
                    'email':user.email,
                    'address':user.address,
                    'firstName':user.firstName,
                    'lastName':user.lastName}}).success(function(data) {
                    callback(data);
                });
        };
        /**
         * Mock SignIn for development
         * when the server is not reachable;
         */
        var mockSignIn = function(callback) {
            self.user = {
                id: "as223asdasegkemwpck4232",
                username:"Max Mustermann"
            }
            self.updateToken('abcdefghiklmnopqurst');
            callback(self.user);
            $rootScope.$broadcast('user_auth_status_changed');
            $log.warn('[Authentication] Mocking login in');
        }

        this.signIn = function(user, callback){

            if (mockServer) {
                return mockSignIn(callback);
            }
            this.signInCustom({
                'username':user.username,
                'password':user.password
            }, callback);

        }
        this.signInCustom = function(params, callback) {

            $http({
                method: "POST",
                url: AppSettings.serverURI + '/connect',
                data: params
            }).success(function(response) {
                    if (response.status == 200) {
                        self.updateToken(response.data.api_access_token);
                        self.fetchCurrentUser();
                        $location.path('/dashboard');
                    }
                    callback(response);
                });

        };




//        ====================================
//        ==Observer pattern
//        ====================================


        var observerCallbacks = [];

        this.registerAuthStatusObserver = function(callback){
            observerCallbacks.push(callback);
        };

        //call this when you know 'foo' has been changed
        var notifyObservers = function(eventData){
            angular.forEach(observerCallbacks, function(callback){
                callback(self.user);
            });
        };





    });