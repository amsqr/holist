function ApiHelper($http, $log, AppSettings){

    this.url =  null;
    var self = this;

    // refresh data on site method.
    self.refresh = null;
    self.$scope = null;
    /**
     * Initializer Method for overview page
     * generic usable
     * @param $scope
     * @param url
     */
    self.setupOverviewPage = function($scope, url){
        self.url = AppSettings.nodeApi + url;
        self.refresh = self.refreshOverview;
        self.$scope = $scope;

    }
    self.refresh = function() {
        self.doHttpRequest(function(err,result){
            if (err) return false;

            $scope.data = result;

        })
    };




    self.doHttpRequest = function(params, cb) {
        params = params || {};
        var defaults = {
            method: "GET",
            url: self.url
        };
        params = _.extend(defaults,params);
        return $http(params).success(function(data) {
                // console.log('[userdata]', data)

            $log.log('[successful http request]',params.url, data);
        }).error(function(err) {
                $log.error('Error on http request', params.url, err);
        });



    };






}