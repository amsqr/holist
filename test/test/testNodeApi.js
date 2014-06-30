/*
 Mocha Tests for user methods
 #############

 To run the tests install mocha:
 > npm install mocha -g

 then run:
 > mocha


 */


//
// assert documentation:        http://chaijs.com/api/assert/
// mocha testing framework:     http://visionmedia.github.io/mocha/
//

var assert = require("chai").assert,
    http = require('http'),
    Promise = require('promise'),
    request = require('request');

var SERVER_URL = ' http://146.185.190.181:49100/';

// ********************************
// Test Autocompletion API Endpoint
// ********************************

describe('/login/basic/authorize', function() {



    it('should not accept the login', function (done) {
        doHttpRequest(SERVER_URL + 'login/basic/authorize?email=simon@fakir.it&password=helloworld')
            .then(function(response){
            assert.equal(404, response.statusCode);
            done();
        });
    });
    it('should create a new user', function (done) {
        var random = Math.random();
        var randomEmail = Math.random() * 1000 + "@gmail.com";


        var data = {
            email:randomEmail,
            password: Math.random().toString(),
            firstname: 'John',
            lastName: 'Doe'
        }

        /**
         * Tests the newly created user
         */
        var testUser = function () {
            doHttpRequest(SERVER_URL + 'login/basic/authorize?email='+data.email+'&password='+data.password)
                .then(function(response){
                    assert.equal(200, response.statusCode);
                    done();
                });
        }
        /**
         * Process after the post request
         * @param res
         */
        var processPostUser = function (res) {
            var data = '';

            res.on('data', function (chunk) {
                data += chunk;
            });

            res.on('end', function () {
                res.data = data;
                assert.equal(200, res.data);
                testUser();
            });
            res.on('error', function(e) {
                console.log('[HTTPREQUEST ERROR]',e);
            });
        }
        /**
         * Create a new usre
         */
        http.post(SERVER_URL + 'user', processPostUser);


    });

});



/**
 *
 * Helper Method to call HTTP request
 * @param url
 * @returns {Promise}
 */
function doHttpRequest(url){
    return new Promise(function(resolve, reject) {
        http.get(url, function (res) {
            var data = '';

            res.on('data', function (chunk) {
                data += chunk;
            });

            res.on('end', function () {
                res.data = data;
                resolve(res);
            });
            res.on('error', function(e) {
                console.log('[HTTPREQUEST ERROR]',e);
                reject(e)
            });
        });
    });
};


