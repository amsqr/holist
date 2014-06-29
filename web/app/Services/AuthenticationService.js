'use strict';

angular.module('App')
    .service('AuthenticationService', function ($rootScope, $location,$http,$log,AppSettings) {


        this.user = null;
        this.userid = null;
        this.token = null;
        var self = this;
        var mockServer = false;


        var redirect_login_page = function() {
            $location.path('/login/');
            $rootScope.$apply();
        }

        this.init = function() {
            var token = localStorage.getItem('accessToken');
            this.userid = localStorage.getItem('userid');
            console.log('stored token: ', token, this.userid);
            if (token == 'null') {
                token = null;
            }
            this.updateToken(token);
            this.fetchCurrentUser();

        };

        this.logout = function () {
            this.updateToken(null, null);
            this.userid = null;
            $rootScope.$broadcast('user_auth_status_changed');
            notifyObservers();

        };

        this.updateToken = function(userid, token) {
            if (!token){
                delete $http.defaults.headers.common['X-Token'];
                delete $http.defaults.headers.common['access_token'];
                localStorage.removeItem('userToken');
                localStorage.removeItem('userid');
                this.token = null;
                return;
            }
            if (token != this.token) {
                console.log('updating token',token);
                this.token = token;
                this.userid = userid;
            }
           // $http.defaults.headers.common['X-Token'] = token;
           // $http.defaults.headers.common['access_token'] = token;

            localStorage.setItem('userid', userid);
            localStorage.setItem('accessToken', token);
        }
        /***
         * fetch the userdata of the current
         * logged in user
         */
        this.fetchCurrentUser = function(){
            // '/users/' + user._id
            if (!this.userid) {
                return false;
            }
            $http({
                method: "GET",
                url: AppSettings.nodeApi + 'users/' + this.userid
            })
                .success(function(data) {
                       this.user = data;
                        // console.log('[userdata]', data)
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
        /**
         * Request a new password for given email
         * @param callback
         * @param email
         */
        this.requestPassword = function(email,callback) {
            $http({
                method: "POST",
                url: AppSettings.nodeApi + 'login/basic/reset_password',
                data: {email:email}
            }).success(function(data) {
                    callback(data);
                });


        }
        this.signUp = function(user, callback) {

            $http({
                method: "POST",
                url: AppSettings.nodeApi + 'user',
                data: user} )
                .success(function(data) {
                    callback(data);
                })
                .error(function(err){
                    callback(err,null);
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
            self.updateToken(1, 'abcdefghiklmnopqurst');
            callback(null, self.user);
            $rootScope.$broadcast('user_auth_status_changed');
            $log.warn('[Authentication] Mocking login in');
        }

        /**
         * external sign in method
         * @param user
         * @param callback
         * @returns {}
         */
        this.signIn = function(user, callback){

            if (mockServer) {
                return mockSignIn(callback);
            }
            this.signInCustom({
                'email':user.email,
                'password':user.password
            }, callback);

        }
        /**
         * sign in with custom attributes
         *
         * @param params
         * @param callback
         */
        this.signInCustom = function(params, callback) {
            var then = function(response, statusCode) {
                console.log('[login response]', response.user.accessTokens[0]);

                switch (statusCode) {
                    case 200:
                        self.updateToken(response.user._id,response.user.accessTokens[0]);
                        self.user = response.user;
                        $rootScope.$broadcast('user_auth_status_changed');
                        callback(null, response);
                        break;
                    case 404:
                        callback('not_found');
                        break;
                    case 400:
                        callback('bad_request');
                        break;
                    default:
                        callback(response);
                        break;
                }

            };

            $http({
                method: "GET",
                url: AppSettings.nodeApi + 'login/basic/authorize?' + $.param(params),
            })
             .success(then)
             .error(then);

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