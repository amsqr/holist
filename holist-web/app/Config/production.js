'use strict';
angular.module('App')
    .constant('AppSettings', {
        debug: false,
        mockhttp: false,
        serverUrl: 'http://localhost:4000', //api
        websiteUri: 'http://localhost:4000',
        appUri: 'http://localhost:9000',
        nodeApi : 'http://holist.pcdowling.com:8080/'

    })
    .constant('angularMomentConfig', {
        preprocess: 'unix', // optional
        timezone: 'Europe/Berlin' // optional
    });
