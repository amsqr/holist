'use strict';
// ['']
angular
    .module('App', [
        'ngResource',
        'ngSanitize',
        'ui.bootstrap',
        'ui.router',
        'angularMoment',
        'ngRetina'
    ])

.config(function($sceDelegateProvider) {
    $sceDelegateProvider.resourceUrlWhitelist(['self', 'http://holist.pcdowling.com/', 'http://api.holist.com/**'])
})
    .config(function($stateProvider, $urlRouterProvider) {

        $stateProvider
            .state('index', {
                url: '/index',
                templateUrl: 'app/Views/index.html',
                controller: 'HomeController'
            })
            .state('about', {
                url: '/about',
                templateUrl: 'app/Views/about.html',
                controller: 'AboutController'
            })
            .state('services', {
                url: '/services',
                templateUrl: 'app/Views/services.html',
                controller: 'ServicesController'
            })
            .state('pricing', {
                url: '/pricing',
                templateUrl: 'app/Views/pricing.html',
            })
            .state('contact', {
                url: '/contact',
                templateUrl: 'app/Views/contact.html',
            })
            .state('signup', {
                url: '/signup',
                templateUrl: 'app/Views/signup.html',
            })
            .state('login', {
                url: '/login',
                templateUrl: 'app/Views/login.html',
                controller: "LoginController"
            })
            .state('logout', {
                url: '/logout',
                templateUrl: 'app/Views/login.html',
                controller: "LoginController"
            })

            .state('blog', {
                url: '/blog',
                templateUrl: 'app/Views/blog.html',
            })
            .state('careers', {
                url: '/careers',
                templateUrl: 'app/Views/careers.html',
            })
            .state('events', {
                url: '/events',
                templateUrl: 'app/Views/events.html',
            })
            .state('faqs', {
                url: '/faqs',
                templateUrl: 'app/Views/faqs.html',
            })
            .state('partners', {
                url: '/partners',
                templateUrl: 'app/Views/partners.html',
            })
            .state('team', {
                url: '/team',
                templateUrl: 'app/Views/team.html',
            })
            .state('privacy', {
                url: '/privacy',
                templateUrl: 'app/Views/privacy.html',
            })
            .state('sitemap', {
                url: '/sitemap',
                templateUrl: 'app/Views/sitemap.html',
            })
            .state('terms', {
                url: '/terms',
                templateUrl: 'app/Views/terms.html',
            })
            .state('imprint', {
                url: '/imprint',
                templateUrl: 'app/Views/imprint.html',
            })
            .state('search', {
                url: '/query/:query',
                templateUrl: 'app/Views/index.html',
                controller: 'HomeController'
            })
            .state('readlist', {
                url: '/readlist',
                templateUrl: 'app/Views/readlist.html',
                controller: 'ReadlistController'
            })
            .state('otherwise', {
                url: 'app/Views/404.html'
            });
    })
    .config(function($urlRouterProvider) {
        // when there is an empty route, redirect to /index
        $urlRouterProvider.when('', '/index');
    });



//
// Chrome bug fix
//
/*
//Chrome passes the error object (5th param) which we must use since it now truncates the Msg (1st param).
window.onerror = function(errorMsg, url, lineNumber, columnNumber, errorObject) {
    var errMsg;
    //check the errorObject as IE and FF don't pass it through (yet)
    if (errorObject && errorObject !== undefined) {
        errMsg = errorObject.message;
    } else {
        errMsg = errorMsg;
    }
    console.log('Error: ' + errMsg);
}
*/