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
        /**
         * Initializes authentication
         */
        this.init = function() {
            var token = localStorage.getItem('accessToken');
            this.userid = localStorage.getItem('userid');
            if (token == 'null') {
                token = null;
            }
            this.updateToken(this.userid, token);
            this.fetchCurrentUser();

        };
        /**
         * Logout the urrent user;
         */
        this.logout = function () {
            this.updateToken(null, null);
            this.userid = null;
            notifyObservers();

        };

        /**
         * Update and store current userid + accesstoken
         * @param userid
         * @param token
         */
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
                self.token = token;
                self.userid = userid;
                self.fetchCurrentUser();
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
            if (!this.userid || this.userid == 'null') {
                return false;
            }

            $http({
                method: "GET",
                url: AppSettings.nodeApi + 'me/?access_token=' + this.token
            })
                .success(function(data) {

                       if (data.user) {
                           self.user = data.user;
                           $rootScope.$broadcast('user_auth_status_changed');
                       }
                        // console.log('[userdata]', data)
                });
        }
        this.getUser = function() {
            return this.user;
        }
        this.isLoggedIn = function() {
            console.log('this.token',this.token)
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
        /**
         *
         * @param user
         * @param callback
         */
        this.signUp = function(user, callback) {

            $http({
                method: "POST",
                url: AppSettings.nodeApi + 'user',
                data: user} )
                .success(function(data) {
                    // console.log('signup data',data.user);
                    var token = (data.user.accessTokens? data.user.accessTokens[0]:null);
                    self.updateToken(data.user._id,token)
                    callback(null, data);
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

                switch (statusCode) {
                    case 200:
                        self.updateToken(response.user._id,response.user.accessTokens[0]);
                        notifyObservers();
                        self.user = response.user;
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
            $rootScope.$broadcast('user_auth_status_changed');

            angular.forEach(observerCallbacks, function(callback){
                callback(self.user);
            });
        };





    });