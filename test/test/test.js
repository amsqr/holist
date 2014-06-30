/*
  Mocha Tests
  for Holist API
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

var SERVER_URL = 'http://holist.pcdowling.com/';

// ********************************
// Test Autocompletion API Endpoint
// ********************************

describe('/autocompletion', function() {

    var testKeyword = function(keyword,test) {
        var url = SERVER_URL + 'complete_search?entityName=' + keyword;
        doHttpRequest(url)
            .then(test)
    }


    it('should respond to keyword App', function (done) {
        testKeyword('App',function(response){
                assert.equal(200, response.statusCode);
                var results = JSON.parse(response.data);
                // array of objects
                assert(results.length > 5, 'number of results');
                done();
        });
    });

    it('should respond to keyword App', function (done) {
        testKeyword('App',function(response){
            assert.equal(200, response.statusCode);
            var results = JSON.parse(response.data);
            // array of objects
            assert(results.length > 5, 'number of results');
            done();
        });
    });


    it('should not throw error on empty request', function (done) {
        testKeyword('',function(response){
            assert.equal(200, response.statusCode);
            var results = JSON.parse(response.data);
            // array of objects
            assert(results.length > 5, 'number of results');
            done();
        });
    });

    it('should not respond to post request', function (done) {
        var url = SERVER_URL + 'complete_search?entityName=Google';

        request.post(url, {}, function (error, res, body) {
            // expcet 405 error on wrong request.
            assert.equal(405, res.statusCode);
            done();
        });

    });



    it('should respond to keyword Google', function (done) {
        testKeyword('Google',function(response){
            assert.equal(200, response.statusCode);
            var results = JSON.parse(response.data);
            assert.ok(results.length > 5, 'number of results are to low');
            done();
        });
    });
    it('should not respond to weird string', function (done) {
        testKeyword('WEIRD-STRING-WITHOUT-SENSE',function(response){
            assert.equal(200, response.statusCode);
            var results = JSON.parse(response.data);
            assert.ok(results.length == 0, 'number of results are to high');
            done();
        });
    });



});



// ********************************
// Test Search / Graph API Endpoint
// ********************************

describe('/search_entity', function() {

    var testKeyword = function(keyword,done) {
        var testUrl = SERVER_URL + 'search_entity?entityName=' + keyword;
        doHttpRequest(testUrl)
            .then(function (res) {
                assert.equal(200, res.statusCode);

                var data = JSON.parse(res.data);
                var mainNode = data.nodes[0];

                assert(mainNode.documents === undefined, 'Main node should have no documents');
                assert(mainNode.title === keyword, 'Main node have the search keyword');
                assert(mainNode.id === 'center', 'Main Node should have the id "center" ');

                done();
            });
    };
    it('should responed to google search', function (done) {
        testKeyword('google',done);
    });
    it('should responed to apple search', function (done) {
        testKeyword('apple', done);
    });
    it('should respond to empty search', function (done) {
        testKeyword('', done);
    });

    //
    // Testcase: Check Document Provider
    // ==================================
    // does a http search request and checks
    // if the response is sensible.
    ///
    it('should provide documents', function (done) {
        var testUrl = SERVER_URL + 'search_entity?entityName=Holist';
        doHttpRequest(testUrl)
            .then(function (res) {

                var data = JSON.parse(res.data);
                var i;

                assert(data.nodes.length > 2, ' should provide more than two documents for the graph');
                for (i in data.nodes) {
                    if (data.nodes[i].id != 'center') {
                        assert.isNotNull(data.nodes[i].documents, ' every node in the graph has to have a document ');
                    }
                    assert.isNotNull(data.nodes[i], ' every node in the graph has to have a document ');
                }
                done();
            });
    });
});

// **************************
// Basic Webserver test
// **************************
describe('/', function () {

    // =======================
    // Test not existing page
    // =======================
    var url  = SERVER_URL + 'randomNotExistingPage';
    it('should return 404', function (done) {
        http.get(url, function (res) {
            assert.equal(404, res.statusCode);
            done();
        })
    });


    // =======================
    // Test existing page
    // =======================
    it('should return 200', function (done) {
        var testUrl = SERVER_URL + 'search_entity?entityName=Google';
        doHttpRequest(testUrl)
            .then(function (res) {
            assert.equal(200, res.statusCode);
            done();
        });
    });

    // test if frontend is availalble

    it('should deliver the Onepage WebApp', function (done) {
        var testUrl = SERVER_URL + 'holist/web/';
        doHttpRequest(testUrl)
            .then(function (res) {
                assert.equal(200, res.statusCode);
                assert.ok( res.data.indexOf('<!DOCTYPE html') !== -1, ' the webapp respone should have a doctype' );
                done();
            });
    });

});


// ****************************
// Test favorites API Endpoint
// ****************************
describe('/favorites', function () {


    it('should save favorite', function (done) {
        var validDocument = '';

        doHttpRequest(SERVER_URL + 'search_entity?entityName=Google')
            .then(function(response){

                assert.equal(200, response.statusCode);

                //
                // find valid document
                //
                var data = JSON.parse(response.data);
                var validDocument = data.nodes[1].documents[0].id || '537537bf1d1d57300fdda721'; // fallback


                var saveUrl = SERVER_URL + 'favorites?document_id=' + validDocument;

                // save document

                request.post(saveUrl, {}, function (error, res, body) {
                    assert.equal(200, res.statusCode);
                    assert.ok(body.indexOf('Ok') !== -1, ' Save Favorite should response ok');
                    done();
                });


            });

    });



    it('should throw error on post favorite', function (done) {

        var url = SERVER_URL + 'favorites';

        request.post(url,{} , function (error, res, body) {
            assert(200 != res.statusCode, 'response code unequal 200 (' + res.statusCode + ')');
            //assert(body.indexOf('exceptions.KeyError') !== -1, 'missing error message in response');
            done();
        });

    });
    it('should show favorite', function (done) {

        var url = SERVER_URL + 'favorites';

        doHttpRequest(url)
            .then(function(response){
                assert.equal(200, response.statusCode);

                var data = JSON.parse(response.data);

                assert(typeof(data.documents) !=='undefined', 'favorites not found');
                assert(data.documents.length > 0, 'Saved Favorites' );


                done();
            });
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

