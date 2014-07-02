/**
 *	holist-server > Article.js
 *	Copyright (c) 2014, Robert Weindl. All rights reserved.
 */


var mongoose = require('mongoose'),
    Schema = mongoose.Schema;

var HTTPStatusCodes = require('../Helpers/HTTPStatusCodes.js');
var Validation = require('../Helpers/Validation.js');

/**
 * 	ArticleSchema.
 */
var ArticleSchema = new Schema({
    //////////////////////////////////////////
    ////////	Article Information  /////////
    //////////////////////////////////////////

    /* The parameter _id is given as default by MongoDB. */
    _id: {
        type: String,
        trim: true,
        required: true,
    }

    /* This is the articles's title. */
    title: {
        type: String,
        trim: true,
        required: false,
        default: ""
    },

    /* This is the articles's description. */
    description: {
        type: String,
        trim: true,
        required: false,
        default: ""
    },

    /* This is the articles's text. */
    text: {
        type: String,
        trim: true,
        required: false,
        default: ""
    },

    /* This is the articles's link. */
    link: {
        type: String,
        trim: true,
        required: false,
        default: ""
    },

    ////////////////////////////////////////////
    ////////	Analytics Information  /////////
    ////////////////////////////////////////////

    /* This is the articles's sourceType. */
    sourceType: {
        type: String,
        trim: true,
        required: false,
        default: ""
    },

    /* This is the timestamp of the article. */
    timestamp: {
        type: Date,
        required: false,
        default: Date.now()
    }
});

/**
 *	 Export the ArticleSchema in order to use it as an Article object.
 */
var Article = mongoose.model('Article', ArticleSchema);
module.exports = Article;
