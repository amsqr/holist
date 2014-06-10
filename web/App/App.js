'use strict';
// ['']
angular
    .module('App', [
         'ui.bootstrap',
    ])

    .config(function($sceDelegateProvider) {
        $sceDelegateProvider.resourceUrlWhitelist(['self','http://api.holist.com/**',])
    })

;


