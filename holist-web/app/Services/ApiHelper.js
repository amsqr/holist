/***
 * Generic helper function for api access
 *
 * This is a generic class to be use for every
 * "basic" crud subsite; e.g. Overview and detail pages.
 *
 * @param $http
 * @param $log
 * @param AppSettings
 * @returns {ApiHelper}
 * @constructor
 */
function ApiHelper($http, $log, AppSettings,$rootScope, AuthenticationService){

    this.url =  null

    var self = this;
    self.accessToken = null;
    self.userid  = null
    self.targetVariable = 'data';

    // refresh data on site method.

    self.$scope = null;
    /**
     * Initializer Method for overview page
     * generic usable
     * @param $scope
     * @param url
     */
    self.setupOverviewPage = function($scope, url, targetVariable){
        self.url = AppSettings.nodeApi + url;
        self.$scope = $scope;
        if (targetVariable){
            self.targetVariable = targetVariable;
        }
        updateToken();
    }

    /***
     * Refesh the data on the current view
     */
    self.refresh = function() {

        var process = function(){
             self.doHttpRequest({},function(err,result){
                 console.log('result favorits',err,  result);
                 if (err) return false;

                self.$scope[self.targetVariable] = result;
                 console.log('favs', self.targetVariable, self.$scope[self.targetVariable]);

            })
        }
        if (!self.accessToken){
            // wait 1 sec for the access token
            window.setTimeout(process, 1000);
            return;
        }
        process();


    };

    /***
     * updateToken
     * > fetches new token form Authentication provider if login status changes..
     */
    var updateToken = function(){
        self.accessToken = AuthenticationService.token;
        self.userid= AuthenticationService.userid;
        if (self.$scope){
            self.$scope.userLoggedIn = AuthenticationService.isLoggedIn();
            console.log('logged in ', self.$scope.userLoggedIn);
        }
    };
    // AuthenticationService.registerAuthStatusObserver(updateToken);
    $rootScope.$on('user_auth_status_changed',updateToken);
    updateToken();

    /**
     * Creates an http request and handles success
     * or error.
     * @todo: could be moved in an seperate API Service.
     *
     * @param params
     * @param cb
     * @returns {Error|*|Promise}
     */
    self.doHttpRequest = function(params, cb) {
        params = params || {};

        //default Values

        if (!params.method) params.method = 'GET';
        if (!params.url) params.url = self.url;
        else params.url = AppSettings.nodeApi + params.url;


        if (!self.accessToken) {
            $log.error('[NO ACCESS TOKEN - is the user logged in?]');
            return;
        }

        params.url += (params.url.indexOf('?') !== -1?'&':'?') + 'access_token=' + self.accessToken;
        if (self.userid) {
            params.url = params.url.replace(/:me/, self.userid);
        }

        return $http(params).success(function(data) {
                // console.log('[userdata]', data)

            $log.log('[successful http request]',params.url, data);
            cb(null,data);
        }).error(function(err) {
                $log.error('Error on http request', params.url, err);
                cb(err,null);
        });



    };


    return self;




}