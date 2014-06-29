/**
*	holist-server > Validation.js
*	Copyright (c) 2014, Robert Weindl. All rights reserved.
*/

/**
 *	Check if a value is undefined.
 * 	@return String with the value if it is not undefined else an empty string.
 */
var validateString = function(value)
{
	return ('undefined' === typeof value) ? '' : value;
};

/**
 *	Check if a value is undefined.
 * 	@return Number with the value if it is not undefined else 0.
 */
var validateNumber = function(value)
{
	return ('undefined' === typeof value) ? 0 : value;
};

/**
 *	Check if an array is undefined.
 *	@return Array with the values if it is not undefined else an empty array.
 */
 var validateArray = function(array)
 {
	if ('undefined' === typeof array)
	{
		return [];
	}
	else
	{
		if (array instanceof Array)
	  	{
			return array;
		}
		else
		{
			return array.split();
		}
	}
 };

/**
 * Creates a random uuid fragment.
 */
var s4 = function()
{
	return Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1);
};

/**
 * Creates a uuid.
 */
var guuid = function()
{
	return s4() + s4() + '-' + s4() + '-' + s4() + '-' + s4() + '-' + s4() + s4() + s4();
};

/**
 *	Create a simple security token.
 */
var simpleSecurityToken = function()
{
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

    for( var i=0; i < 4; i++ )
	{
		text += possible.charAt(Math.floor(Math.random() * possible.length));
	}

    return text;
};

/**
*	Create a strong security token.
*/
var strongSecurityToken = function(length)
{
	var text = "";
	var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~";

	for( var i=0; i < length; i++ )
	{
		text += possible.charAt(Math.floor(Math.random() * possible.length));
	}

	return text;
};

module.exports.validateString = validateString;
module.exports.validateArray = validateArray;
module.exports.validateNumber = validateNumber;
module.exports.simpleSecurityToken = simpleSecurityToken;
module.exports.strongSecurityToken = strongSecurityToken;
module.exports.s4 = s4;
module.exports.guuid = guuid;
