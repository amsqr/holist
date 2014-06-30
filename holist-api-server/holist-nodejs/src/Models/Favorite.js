/**
 *	holist-server > Favorite.js
 *	Copyright (c) 2014, Robert Weindl. All rights reserved.
 */


var mongoose = require('mongoose'),
    Schema = mongoose.Schema;
var async = require('async');

var HTTPStatusCodes = require('../Helpers/HTTPStatusCodes.js');
var Validation = require('../Helpers/Validation.js');

/**
 * 	FavoriteSchema.
 */
var FavoriteSchema = new Schema({
    ///////////////////////////////////////////
    ////////	Favorite Information  /////////
    ///////////////////////////////////////////

    /* The parameter _id is given as default by MongoDB. */

    /* The favorite's user. */
    user: {
        type: Schema.Types.ObjectId,
        ref: 'User',
        required: true,
        index: true
    },

    /* The favorite's id */
    // [TODO] Replace favorite type string with the favorite object as soon the REST API is using the same database as the lexical and semantic algorithms.
    favorite: {
        type: String,
        trim: true,
        required: true,
        index: true
    },

    ////////////////////////////////////////////
    ////////	Analytics Information  /////////
    ////////////////////////////////////////////

    /* This is the date of the creation of the favorite. */
    createdDate: {
        type: Date,
        required: true,
        default: Date.now()
    }
});

/**
 *	Create a new favorite.
 *
 *	@param userID The favorite's user _id.
 *  [TODO] Replace favoriteID with the favorite object as soon the REST API is using the same database as the lexical and semantic algorithms.
 *	@param favoriteID The favorite's id.
 *
 *	@return callback(error, favorite, status)
 */
FavoriteSchema.statics.createFavorite = function(userID, favoriteID, callback) {
    if ('' !== Validation.validateString(userID) &&
        '' !== Validation.validateString(favoriteID)) {
        mongoose.models["Favorite"]
            .findOne({
                favorite: favoriteID
            })
            .exec(function(err, favorite) {
                if (err) {
                    return callback(err, null, HTTPStatusCodes.HTTPStatusCode500InternalServerError);
                }
                if (favorite) {
                    return callback(null, null, HTTPStatusCodes.HTTPStatusCode409Conflict);
                } else {
                    // Create the favorite.
                    var favorite = new Favorite({
                        user: userID,
                        favorite: favoriteID,
                        creationDate: Date.now()
                    });

                    // Save and return the favorite.
                    favorite.save(function(err, event) {
                        if (err) {
                            return callback(err, null, HTTPStatusCodes.HTTPStatusCode500InternalServerError);
                        }

                        return callback(null, favorite, HTTPStatusCodes.HTTPStatusCode201Created);
                    });
                }
            });
    } else {
        return callback(null, null, HTTPStatusCodes.HTTPStatusCode400BadRequest);
    }
};

/**
 *	Get all favorites for a user.
 *
 *	@param user The favorite's user object.
 *
 *	@return callback(error, favorites, status)
 */
FavoriteSchema.statics.getFavoritesForUser = function(user, callback) {
    if ('' !== Validation.validateString(user)) {
        mongoose.models["Favorite"]
            .find({
                user: user._id
            })
            .select('_id favorite createdDate')
            .exec(function(err, favorites) {
                if (err) {
                    return callback(err, null, HTTPStatusCodes.HTTPStatusCode500InternalServerError);
                }
                if (favorites) {
                    return callback(null, favorites, HTTPStatusCodes.HTTPStatusCode200OK);
                } else {
                    return callback(null, null, HTTPStatusCodes.HTTPStatusCode404NotFound);
                }
            });
    } else {
        return callback(null, null, HTTPStatusCodes.HTTPStatusCode400BadRequest);
    }
};

/**
 *	 Export the FavoriteSchema in order to use it as an Favorite object.
 */
var Favorite = mongoose.model('Favorite', FavoriteSchema);
module.exports = Favorite;