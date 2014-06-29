'use strict';
angular.module('App')
    .constant('AppSettings', {
        debug: true,
        mockhttp: false,
        apiUrl: 'http://holist.pcdowling.com/', //api
        websiteUri: 'http://localhost:4000',
        appUri: 'http://localhost:9000',
        nodeApi : 'http://146.185.190.181:49100/'


    })
    .constant('angularMomentConfig', {
        preprocess: 'unix', // optional
        timezone: 'Europe/Berlin' // optional
    });
