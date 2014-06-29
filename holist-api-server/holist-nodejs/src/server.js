#!/bin/env node

/**
 *	holist-server > server.js
 *	Copyright (c) 2014, Robert Weindl. All rights reserved.
 */

/* Include all used modules. */
var express = require('express');
var bodyParser = require('body-parser');
var http = require('http');
var mongoose = require('mongoose');
var HTTPStatusCodes = require('./Helpers/HTTPStatusCodes.js');
var Validation = require('./Helpers/Validation.js');
var url = require('url');

/**
 * 	Include MongoDB schemes.
 */
var Schema = mongoose.Schema;
var User = require('./Models/User.js')
var Favorite = require('./Models/Favorite.js')

/**
 *  Implementation of the HolistServer application.
 */
var HolistServer = function() {
    //  Scope.
    var self = this;

    /*  ===============================================================  */
    /*  Server Environment, Initialization & Helper functions            */
    /*  ===============================================================  */

    /**
     *  Setup application specific variables.
     */
    self.setupVariables = function() {
        // Port
        self.port = 8080;

        // MongoDB
        var address = process.env.HOLISTMONGODB_PORT_27017_TCP_ADDR;
        var port = process.env.HOLISTMONGODB_PORT_27017_TCP_PORT;
        self.mongodbAddress = "mongodb://" + address + ":" + port + "/holist-nodejs";
    };

    /**
     *  terminator === the termination handler
     *  Terminate server on receipt of the specified signal.
     *  @param {string} sig  Signal to terminate on.
     */
    self.terminator = function(sig) {
        if (typeof sig === "string") {
            console.log('%s: Received %s - Terminating holist server.',
                Date(Date.now()), sig);
            process.exit(1);
        }
        console.log('%s: holist server stopped.', Date(Date.now()));
    };

    /**
     *  Setup termination handlers (for exit and a list of signals).
     */
    self.setupTerminationHandlers = function() {
        //  Process on exit and signals.
        process.on('exit', function() {
            self.terminator();
        });

        // Removed 'SIGPIPE' from the list - bugz 852598.
        ['SIGHUP', 'SIGINT', 'SIGQUIT', 'SIGILL', 'SIGTRAP', 'SIGABRT',
            'SIGBUS', 'SIGFPE', 'SIGUSR1', 'SIGSEGV', 'SIGUSR2', 'SIGTERM'
        ].forEach(function(element, index, array) {
            process.on(element, function() {
                self.terminator(element);
            });
        });
    };

    /**
     *  Initializes the HolistServer application.
     */
    self.initialize = function() {
        // Initialize the server environment.
        self.setupVariables();
        self.setupTerminationHandlers();

        // Initialize the database connection.
        self.initializeDatabaseConnection();

        // Initialize the express server and routes.
        self.initializeNodeServer();
    };

    /**
     *  Initialize the server (express) and create the routes and register
     *  the handlers.
     */
    self.initializeNodeServer = function() {
        // Initialization of express.
        self.app = express();

        // Configure the application.
        self.app.use(function(req, res, next) {
            res.setHeader("Access-Control-Allow-Origin", "*");
            return next();
        });
        self.app.use(bodyParser.json());


        self.http = http.createServer(self.app);
        self.initializePublicRoutes();
        self.initializePrivateRoutes();
    };

    /**
     *    Initialize all public routes.
     */
    self.initializePublicRoutes = function() {
        // Initialize all public route arrays.
        self.createPublicGetRoutes();
        self.createPublicPostRoutes();
        self.createPublicPutRoutes();
        self.createPublicDeleteRoutes();

        // Add public GET handlers for the app.
        for (var g in self.getPublicRoutes) {
            self.app.get(g, self.getPublicRoutes[g]);
        }

        // Add public POST handlers for the app.
        for (var p in self.postPublicRoutes) {
            self.app.post(p, self.postPublicRoutes[p]);
        }

        // Add public PUT handlers for the app.
        for (var p in self.putPublicRoutes) {
            self.app.put(p, self.putPublicRoutes[p]);
        }

        // Add public DELETE handlers for the app.
        for (var d in self.deletePublicRoutes) {
            self.app.delete(d, self.deletePublicRoutes[d]);
        }
    };

    /**
     *    Initialize all private routes.
     */
    self.initializePrivateRoutes = function() {
        // Initialize all private route arrays.
        self.createPrivateGetRoutes();
        self.createPrivatePostRoutes();
        self.createPrivatePutRoutes();
        self.createPrivateDeleteRoutes();

        // Add prviate GET handlers for the app.
        for (var g in self.getPrivateRoutes) {
            self.app.get(g, self.authenticate(), self.getPrivateRoutes[g]);
        }

        // Add prviate POST handlers for the app.
        for (var p in self.postPrivateRoutes) {
            self.app.post(p, self.authenticate(), self.postPrivateRoutes[p]);
        }

        // Add prviate PUT handlers for the app.
        for (var p in self.putPrivateRoutes) {
            self.app.put(p, self.authenticate(), self.putPrivateRoutes[p]);
        }

        // Add prviate DELETE handlers for the app.
        for (var d in self.deletePrivateRoutes) {
            self.app.delete(d, self.authenticate(), self.deletePrivateRoutes[d]);
        }
    }

    /**
     *	Initialize the database (mongoose) and create the database connection.
     */
    self.initializeDatabaseConnection = function() {
        // Create database connection.
        mongoose.connect(self.mongodbAddress);

        // Configure the mongoose callbacks.
        self.db = mongoose.connection;
        self.db.on('error', console.error.bind(console, 'connection error:'));
        self.db.once('open', function callback() {
            console.log('Created connection to the database ...');
        });
    };

    /*  ================================================================  */
    /*  App server functions (main app logic here).                       */
    /*  ================================================================  */

    /**
     *  Error handler.
     */
    self.handleError = function(res, err, status) {
        console.error(err);
        return res.send(status);
    };

    /**
     *  Middleware to authenticate against the server.
     *  A access token is needed.
     */
    self.authenticate = function() {
        return function(req, res, next) {
            // Extract and validate the access token.
            var queryParameters = url.parse(req.url, true);
            var accessToken = queryParameters.query.access_token;

            if ('' === Validation.validateString(accessToken)) {
                return res.send(HTTPStatusCodes.HTTPStatusCode401Unauthorized);
            }

            // Authenticate the user with the given access token.
            User.authenticateWithAccessToken(accessToken, function(err, user, status) {
                if (err) {
                    self.handleError(res, err, status);
                }

                if (user) {
                    console.log(user);
                    req.user = user;
                    next();
                } else {
                    return res.send(HTTPStatusCodes.HTTPStatusCode401Unauthorized);
                }
            });
        };
    };


    //////////////////////////////
    ////////	Public  //////////
    //////////////////////////////

    /**
     *  Create the public GET routing table entries + handlers for the application.
     */
    self.createPublicGetRoutes = function() {
        self.getPublicRoutes = {};

        self.getPublicRoutes['/'] = function(req, res) {
            return res.send('This is holist!');
        };

        self.getPublicRoutes['/login/basic/authorize'] = function(req, res) {
            // Extract the email and password.
            var queryParameters = url.parse(req.url, true);
            var email = queryParameters.query.email;
            var password = queryParameters.query.password;

            User.authenticateWithBasicStrategy(email, password, function(err, user, status) {
                if (err) {
                    return self.handleError(res, err, status);
                }
                if (user) {
                    res.location('http://' + req.headers.host + '/users/' + user._id);
                    return res.send(status, {
                        'user': user
                    });
                } else {
                    return res.send(status);
                }
            });
        };
    };

    /**
     *  Create the public POST routing table entries + handlers for the application.
     */
    self.createPublicPostRoutes = function() {
        self.postPublicRoutes = {};

        self.postPublicRoutes['/user'] = function(req, res) {

            User.createUser(req.body.email, req.body.password, req.body.firstName, req.body.lastName, function(err, user, status) {
                if (err) {
                    return self.handleError(res, err, status);
                }
                if (user) {
                    res.location('http://' + req.headers.host + '/users/' + user._id);
                    return res.send(status, {
                        'user': user
                    });
                } else {
                    return res.send(status);
                }
            });
        };
    };

    /**
     *	Create the public PUT routing table entries + handlers for the application.
     */
    self.createPublicPutRoutes = function() {
        self.putPublicRoutes = {};
    };

    /**
     *	Create the public DELETE routing table entries + handlers for the application.
     */
    self.createPublicDeleteRoutes = function() {
        self.deletePublicRoutes = {};
    };

    //////////////////////////////
    ////////	Private  /////////
    //////////////////////////////
    // Always use req.device.user to get the current user and not ":userid"

    /**
     *  Create the private GET routing table entries + handlers for the application.
     */
    self.createPrivateGetRoutes = function() {
        self.getPrivateRoutes = {};

        self.getPrivateRoutes['/me'] = function(req, res) {
            User.getCurrentAuthenticatedUser(req.user._id, function(err, user, status) {
                if (err) {
                    return self.handleError(res, err, status);
                }
                if (user) {
                    return res.send(status, {
                        'user': user
                    });
                } else {
                    return res.send(status);
                }
            });
        };

        self.getPrivateRoutes['/users/:userid/favorites'] = function(req, res) {
            Favorite.getFavoritesForUser(req.user, function(err, favorites, status) {
                if (err) {
                    return self.handleError(res, err, status);
                }

                if (favorites) {
                    return res.send(status, {
                        'favorites': favorites
                    });
                } else {
                    return res.send(status);
                }
            });
        };
    };

    /**
     *  Create the private POST routing table entries + handlers for the application.
     */
    self.createPrivatePostRoutes = function() {
        self.postPrivateRoutes = {};

        self.postPrivateRoutes['/users/:userid/favorite'] = function(req, res) {
            Favorite.createFavorite(req.user._id, req.body.favoriteID, function(err, favorite, status) {
                if (err) {
                    return self.handleError(res, err, status);
                }
                if (favorite) {
                    res.location('http://' + req.headers.host + '/users/' + req.user._id + '/favorites/' + favorite._id);
                    return res.send(status, {
                        'favorite': favorite
                    });
                } else {
                    return res.send(status);
                }
            });
        }
    };

    /**
     *	Create the private PUT routing table entries + handlers for the application.
     */
    self.createPrivatePutRoutes = function() {
        self.putPrivateRoutes = {};
    };

    /**
     *	Create the private DELETE routing table entries + handlers for the application.
     */
    self.createPrivateDeleteRoutes = function() {
        self.deletePrivateRoutes = {};
    };

    /*  ===============================================================  */
    /*  Server Execution                                                 */
    /*  ===============================================================  */

    /**
     *  Start the server (start up the HolistServer application).
     */
    self.start = function() {
        // Start the app on the specific interface (and port).
        self.http.listen(self.port, function() {
            console.log('%s: holist server started.', Date(Date.now()));
        });
    };
}; /*  End of HolistServer */


/**
 *	main(s): Initialize and start the HolistServer application.
 */
var _holistServer = new HolistServer();
_holistServer.initialize();
_holistServer.start();
