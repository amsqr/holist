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
                templateUrl: 'App/Views/index.html',
                controller: 'HomeController'
            })
            .state('about', {
                url: '/about',
                templateUrl: 'App/Views/about.html',
                controller: 'AboutController'
            })
            .state('services', {
                url: '/services',
                templateUrl: 'App/Views/services.html',
                controller: 'ServicesController'
            })
            .state('pricing', {
                url: '/pricing',
                templateUrl: 'App/Views/pricing.html',
            })
            .state('contact', {
                url: '/contact',
                templateUrl: 'App/Views/contact.html',
            })
            .state('signup', {
                url: '/signup',
                templateUrl: 'App/Views/signup.html',
            })
            .state('login', {
                url: '/login',
                templateUrl: 'App/Views/login.html',
                controller: "LoginController"
            })
            .state('blog', {
                url: '/blog',
                templateUrl: 'App/Views/blog.html',
            })
            .state('careers', {
                url: '/careers',
                templateUrl: 'App/Views/careers.html',
            })
            .state('events', {
                url: '/events',
                templateUrl: 'App/Views/events.html',
            })
            .state('faqs', {
                url: '/faqs',
                templateUrl: 'App/Views/faqs.html',
            })
            .state('partners', {
                url: '/partners',
                templateUrl: 'App/Views/partners.html',
            })
            .state('team', {
                url: '/team',
                templateUrl: 'App/Views/team.html',
            })
            .state('privacy', {
                url: '/privacy',
                templateUrl: 'App/Views/privacy.html',
            })
            .state('sitemap', {
                url: '/sitemap',
                templateUrl: 'App/Views/sitemap.html',
            })
            .state('terms', {
                url: '/terms',
                templateUrl: 'App/Views/terms.html',
            })
            .state('imprint', {
                url: '/imprint',
                templateUrl: 'App/Views/imprint.html',
            })
            .state('search', {
                url: '/query/:query',
                templateUrl: 'App/Views/index.html',
                controller: 'HomeController'
            })
            .state('readlist', {
                url: '/readlist',
                templateUrl: 'App/Views/readlist.html',
                controller: 'ReadlistController'
            })
            .state('otherwise', {
                url: 'App/Views/404.html'
            });
    })
    .config(function($urlRouterProvider) {
        // when there is an empty route, redirect to /index
        $urlRouterProvider.when('', '/index');
    });



//
// Chrome bug fix
//

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
