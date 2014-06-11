'use strict';
angular.module('App')
    .constant('AppSettings', {
        debug: false,
        mockhttp: false,
        serverUrl: 'http://localhost:4000', //api
        websiteUri: 'http://localhost:4000',
        appUri: 'http://localhost:9000'

    })
    .constant('angularMomentConfig', {
        preprocess: 'unix', // optional
        timezone: 'Europe/Berlin' // optional
    });
