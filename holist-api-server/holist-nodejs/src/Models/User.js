/**
 *	holist-server > User.js
 *	Copyright (c) 2014, Robert Weindl. All rights reserved.
 */


var mongoose = require('mongoose'),
	Schema = mongoose.Schema;
var async = require('async');

var HTTPStatusCodes = require('../Helpers/HTTPStatusCodes.js');
var Validation = require('../Helpers/Validation.js');

/**
 * 	UserSchema.
 */
var UserSchema = new Schema({
	///////////////////////////////////////
	////////	User Information  /////////
	///////////////////////////////////////

	/* The parameter _id is given as default by MongoDB. */

	/* This is the users' first name. */
	firstName: {
		type: String,
		trim: true,
		required: false,
		default: ""
	},

	/* This is the user's last name. */
	lastName: {
		type: String,
		trim: true,
		required: false,
		default: ""
	},

	/* This is the user's email. */
	email: {
		type: String,
		trim: true,
		required: true,
		index: true,
		default: ""
	},

	/* This is the user's password. */
	// [TODO] Use bcrypt in the future to encrypt the password!
	password: {
		type: String,
		trim: true,
		required: true,
		index: true,
		default: ""
	},

	/* This is the user's access token. */
	accessTokens: [{
		type: String,
		trim: true,
		required: false,
		index: true
	}],

	/* This are all user favorite articles and graph nodes. */
	favorites: [{
		type: String,
		trim: true,
		required: false
	}],

	////////////////////////////////////////////
	////////	Analytics Information  /////////
	////////////////////////////////////////////

	/* This is the user's last visited date. */
	lastVisitedDate: {
		type: Date,
		required: true,
		default: Date.now()
	},

	/* This is the date of the registration of the user. */
	createdDate: {
		type: Date,
		required: true,
		default: Date.now()
	}
});

/**
 *	Create a new user.
 *
 *	@param email The user's email.
 *	@param password The user's password.
 *  @param firstName The user's firstName.
 *  @param lastName The user's lastName.
 *
 *	@return callback(error, user, status)
 */
UserSchema.statics.createUser = function(email, password, firstName, lastName, callback) {
	if ('' !== Validation.validateString(email) &&
		'' !== Validation.validateString(password)) {
		mongoose.models["User"]
			.findOne({
				email: email
			})
			.exec(function(err, user) {
				if (err) {
					return callback(err, null, HTTPStatusCodes.HTTPStatusCode500InternalServerError);
				}
				if (user) {
					return callback(null, null, HTTPStatusCodes.HTTPStatusCode409Conflict);
				} else {
					// Create the user.
					var user = new User({
						email: email,
						password: password,
						firstName: Validation.validateString(firstName),
						lastName: Validation.validateString(lastName),
						lastVisitedDate: Date.now(),
						createdDate: Date.now()
					});

					// Create an access token.
					user.accessTokens.push(Validation.strongSecurityToken());

					// Save and return the user.
					user.save(function(err, event) {
						if (err) {
							return callback(err, null, HTTPStatusCodes.HTTPStatusCode500InternalServerError);
						}

						// User with the given access token exists. Authentication was successful.
						// Return user object with limited information.
						mongoose.models['User']
							.findOne({
								_id: user._id
							})
							.select('_id firstName lastName email createdDate')
							.exec(function(err, user) {
								if (err) {
									return callback(err, null, HTTPStatusCodes.HTTPStatusCode500InternalServerError);
								}
								return callback(null, user, HTTPStatusCodes.HTTPStatusCode201Created);
							});
					});
				}
			});
	} else {
		return callback(null, null, HTTPStatusCodes.HTTPStatusCode400BadRequest);
	}
};

/**
*	Authenticate a user with basic strategy.
*
*	@param email The user's email adress.
*	@param password The user's password.
*
*	@return callback(error, user, status)
*/
UserSchema.statics.authenticateWithBasicStrategy = function(email, password, callback) {
	if ('' !== Validation.validateString(email) &&
		'' !== Validation.validateString(password)) {
		mongoose.models['User']
			.findOne({
				email: email,
				password: password
			})
			.select('_id firstName lastName email accessTokens createdDate')
			.exec(function(err, user) {
				if (err) {
					return callback(err, null, HTTPStatusCodes.HTTPStatusCode500InternalServerError);
				}

				if (user) {
					user.lastVisitedDate = Date.now();
					user.save(function(err, user) {
						if (err) {
							return callback(err, null, HTTPStatusCodes.HTTPStatusCode500InternalServerError);
						}
						return callback(null, user, HTTPStatusCodes.HTTPStatusCode200OK);
					});
				} else {
					return callback(null, null, HTTPStatusCodes.HTTPStatusCode404NotFound);
				}
			});
	} else {
		return callback(null, null, HTTPStatusCodes.HTTPStatusCode400BadRequest);
	}
};

/**
 *	Authenticate a user with his access token.
 *
 *	@param id The user's access token.
 *
 *	@return callback(error, user, status)
 */
UserSchema.statics.authenticateWithAccessToken = function(accessToken, callback) {
	if ('' !== Validation.validateString(accessToken)) {
		mongoose.models['User']
			.findOne({
				accessTokens: accessToken
			})
			.exec(function(err, user) {
				if (err) {
					return callback(err, null, HTTPStatusCodes.HTTPStatusCode500InternalServerError);
				}

				if (user) {
					user.lastVisitedDate = Date.now();
					user.save(function(err, user) {
						if (err) {
							return callback(err, null, HTTPStatusCodes.HTTPStatusCode500InternalServerError);
						}
						return callback(null, user, HTTPStatusCodes.HTTPStatusCode200OK);
					});
				} else {
					return callback(null, null, HTTPStatusCodes.HTTPStatusCode404NotFound);
				}
			});
	} else {
		return callback(null, null, HTTPStatusCodes.HTTPStatusCode400BadRequest);
	}
};

/**
 *	Returns the current authenticated user.
 *
 *	@param id The user's id.
 *
 *	@return callback(error, user, status)
 */
UserSchema.statics.getCurrentAuthenticatedUser = function(id, callback) {
	if ('' !== Validation.validateString(id)) {
		mongoose.models['User']
			.findOne({
				_id: id
			})
			.select('_id firstName lastName email createdDate')
			.exec(function(err, user) {
				if (err) {
					return callback(err, null, HTTPStatusCodes.HTTPStatusCode500InternalServerError);
				}

				if (user) {
					return callback(null, user, HTTPStatusCodes.HTTPStatusCode200OK);
				} else {
					return callback(null, null, HTTPStatusCodes.HTTPStatusCode404NotFound);
				}
			});
	} else {
		return callback(null, null, HTTPStatusCodes.HTTPStatusCode404NotFound);
	}
};

/**
 *	 Export the UserSchema in order to use it as an User object.
 */
var User = mongoose.model('User', UserSchema);
module.exports = User;
