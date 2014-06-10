'use strict';
// ['']
angular
    .module('App', [
//        'ngCookies',
        'ngResource',
        'ngSanitize',
        'ui.bootstrap',

        'ui.router',
        'angularMoment'


    ])

    .config(function($sceDelegateProvider) {
        $sceDelegateProvider.resourceUrlWhitelist(['self','http://holist.pcdowling.com/','http://api.holist.com/**'])
    })
    .config(function($stateProvider, $urlRouterProvider){

        $stateProvider
            .state('home',  {
                url:        '/index',
                templateUrl:'App/Views/home.html',
                controller: "HomeController"
            })
            .state('search',  {
                url:        '/query/:query',
                templateUrl:'App/Views/home.html',
                controller: "HomeController"
            })
            .state('readlist',  {
                url:        '/readlist',
                templateUrl:'App/Views/readlist.html',
                controller: "ReadlistController"
            })


            .state('login',  {
                url:        '/login',
                templateUrl:'App/Views/login.html',
                controller: "LoginController"
            })


            .state('about',  {
                url:        '/about',

                templateUrl:'App/Views/about.html'
            })

            .state("otherwise", { url : 'App/Views/404.html'});


    })
    .config(function($urlRouterProvider){
        // when there is an empty route, redirect to /index
        $urlRouterProvider.when('', '/index');
    });



//
// Chrome bug fix
//

//Chrome passes the error object (5th param) which we must use since it now truncates the Msg (1st param).
window.onerror = function (errorMsg, url, lineNumber, columnNumber, errorObject) {
    var errMsg;
    //check the errorObject as IE and FF don't pass it through (yet)
    if (errorObject && errorObject !== undefined) {
        errMsg = errorObject.message;
    }
    else {
        errMsg = errorMsg;
    }
    console.log('Error: ' + errMsg);
}


