#holist REST API Reference

## Overview

### General Concepts
- **[Introduction](#introduction)**
- **[Setup](#setup)**
- **[Base IP](#base_ip)**
- **[Authentication](#authentication)**
 - [HTTPS](#authentication_https)
 - [Basic Authentication](#authentication_basic)
 - [Access Token](#access_token)
 
### Resources
- **[User](#users)**
 - [Create a user](#users_create)
 - [Get authenticated user](#users_get_authenticated)
  
- **[Favorites](#favorites)**
 - [Create a favorite](#favorites_create) 
 - [Get multiple favorites](#favorites_get_multiple)

## General Concepts

### <a id="introduction"></a> Introduction
The following document describes the current status of the holist REST  API. All described routes are implemented and tested. In order to guarantee a successful server communication please stick to the documentation. 

### <a id="setup"></a> Setup
In order to automatically setup the complete server infrastructure install the program `docker`. Afterwards just run the `install.sh` script in the root directory of your server. The installation will result in two virtual machines. One virtual machines is for the Node.js application and the other one for the MongoDB. 

In case of any questions about the docker program or the installation script please contact: `robert.weindl@cdtm.de`

### <a id="ports"></a> Ports
The installation will expose two ports: 

|Port   | Description         |
|-------|---------------------|
|`49100`| Node.js Application |
|`49101`| MongoDB 			  |


### <a id="base_ip"></a> Base IP
All URLs referenced in this API documentation begin with the following IP:
```
146.185.190.181
```
This IP is used for the development system. Please also use this IP with one of the specified ports above. In a future version of the holist REST API the  IP will be replaced with a Base URL.


### <a id="authentication"></a> Authentication
Every request to the holist REST API must be authenticated with an API key over HTTP in development and HTTPS in production.


### <a id="authentication_https"></a> HTTPS
In order to provide a sufficient level of security, only a secure (TLS) communication is allowed when communicating with the production API.

`Attention: The development system is not supporting HTTPS.`

### <a id="authentication_basic"></a>Basic Authentication
Before a access token can be used the user has to login using a simple basic authentication approach. In the response the user receives a user object containing an array with access tokens. One of these access tokens have to be used for further private communication with the server.

```
HTTP basic username: email
HTTP basic password: password
```
#### Parameters
| Key                        | Value                                       |
|----------------------------|---------------------------------------------|
| **email**<br /> _required_  | The email for the user.|
| **password**<br /> _required_  | The password for the user.|

###### Example Request:
```
GET http://146.185.190.181:49100/login/basic/authorize?email=<email>&password=<password>
```

###### Example Response
```
HTTP/1.1 200 OK
Location: http://146.185.190.181:49100/users/507f191e810c19729de860ea
{
	"user": {
		"_id": "53b0164f9fa99c010047c6e9",	
		"email": "peter.dinklage@holist.de",
		"lastName": "Dinklage",
		"firstName": "Peter",
		"accessTokens": [
			"<access_token>",
			"<access_token>",
			...			
		],
		"createdDate":"2014-06-29T13:42:32.021Z"
	}
}
```

###### CURL
```
curl -i -X GET 'http://146.185.190.181:49100/login/basic/authorize?email=<email>&password=<password>'
```
###### ERROR RESPONSES
| Code               | Description                                          |
|--------------------|-------------------------------|
| `400 BAD REQUEST`  | The request body is malformed.                       |
| `404 NOT FOUND`	 | A user with the provided email and password does not exists.
| `500 INTERNAL SERVER ERROR` | Internal Server error.

### <a id="access_token"></a> Access Token
After a successful basic authentication the server will respond with an array of valid access tokens for the registered user. For all future requests one of the access tokens has to be provided while communicating with the server.

#### Parameters
| Key                        | Value                                       |
|----------------------------|---------------------------------------------|
| **access_token**<br /> _required_  | The access token for the authenticated user.|


## Resources

### <a id="users"></a> Users
Many of the resources on this API endpoint, provide information about the currently authenticated user. By requesting a resource URL that includes a `:userid` parameter, the response will be for the requested user. In the case, that the endpoint is not a public REST endpoint the `user` for the given authentication credentials will be used instead.

A User can be stored in the MongoDB database. Everything in Mongoose starts with a schema. Each schema maps to a MongoDB collection and defines the shape of the documents within that collection. The UserSchema defines the shape of all user related data.

```
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
 *	 Export the UserSchema in order to use it as an User object.
 */
var User = mongoose.model('User', UserSchema);
module.exports = User;
```

---

#### <a id="users_create"></a> Create a user
This REST endpoint is `public`.

###### URI
```
POST http://146.185.190.181:49100/user
```
###### Body
| Key                            | Value                                                                                                                      |
|--------------------------------|-------------------------------------------|
| **email**<br /> _required_     | New **string** value for the user's email.
| **password**<br /> _required_ | New **string** value for the user's password. |
| **firstName**<br /> _optional_ | New **string** value for the user's first name. |
| **lastName**<br /> _optional_ | New **string** value for the user's last name. |

###### Example Request:
```
POST http://146.185.190.181:491000/user
Content-Type: application/json
{
	"email" : "peter.dinklage@holist.de",
	"password" : "SuperPassword1!",
	"firstName" : "Peter",
	"lastName" : "Dinklage"
}
```

###### Example Response
```
HTTP/1.1 201 Created
Location: http://146.185.190.181:49100/users/507f191e810c19729de860ea

{
	"user": {
		"_id": "53b0164f9fa99c010047c6e9",	
		"email": "peter.dinklage@holist.de",
		"lastName": "Dinklage",
		"firstName": "Peter",
		"createdDate":"2014-06-29T13:42:32.021Z"
	}
}
```

###### CURL
```
curl -i -X POST -H "Content-type: application/json" -d '{"email":"peter.dinklage@holist.de", "password":"SuperPassword1!", "firstName":"Peter", "lastName":"Dinklage"}' http://146.185.190.181:49100/user
```

###### ERROR RESPONSES
| Code               | Description                                          |
|--------------------|-------------------------------|
| `400 BAD REQUEST`  | The request body is malformed.                       |
| `409 CONFLICT`	 | A user with the provided email already exists.
| `500 INTERNAL SERVER ERROR` | Internal Server error.
---

#### <a id="users_get_authenticated"></a> Get authenticated user

This REST endpoint is `private`.


###### URI
```
GET http://146.185.190.181:49100/me
```

###### Parameters
| Key                        | Value                                       |
|----------------------------|---------------------------------------------|
| **access_token**<br /> _required_  | The access token for the authenticated user. |

###### Example Request:
```
GET http://146.185.190.181:49100/me?access_token=<access_token>
```

###### Example Response
```
HTTP/1.1 200 OK
Content-Type: application/json; charset=UTF-8

{
	"user":
	{
	    "_id" : "507f191e810c19729de860ea",
	    "email" : "peter.dinklage@holist.de",
	    "firstName" : "Peter",
	    "lastName" : "Dinklage",
	    "accessTokens" : 
	    [
	    	"<access_token>",
	    	"<access_token>",
	    	...
	    ],
		"creationDate" : "2013-12-17T18:38:51.778Z"
	}
}
```

###### CURL
```
curl -i -X GET 'http://146.185.190.181:49100/me?access_token=<access_token>'
```

###### ERROR RESPONSES
| Code               | Description                                                                        |
|--------------------|------------------------------------------------------------------------------------|
| `400 BAD REQUEST`  | The request parameters are malformed.  
| `401 UNAUTHORIZED` | Authentication credentials are required to access the resource.                    |                                            
| `404 NOT FOUND`    | The user could not be found.
| `500 INTERNAL SERVER ERROR` | Internal Server error.

---

### <a id="favorites"></a> Favorites
`Attention: When connecting to the MongoDB of the lexical and semantic analysis algorithms this document have to be adapted! Currently, a wrapper for simulating favorite ids is implemented.`

A Favorite can be stored in the MongoDB database. Everything in Mongoose starts with a schema. Each schema maps to a MongoDB collection and defines the shape of the documents within that collection. The FavoriteSchema defines the shape of all favorites related data.

```
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
 *	 Export the FavoriteSchema in order to use it as an Favorite object.
 */
var Favorite = mongoose.model('Favorite', FavoriteSchema);
module.exports = Favorite;
```

---
#### <a id="favorites_create"></a> Create a favorite

This REST endpoint is private.

###### URI
```
POST http://146.185.190.181:49100/users/:userid/favorite
```

###### Parameters
| Key                        | Value                                       |
|----------------------------|---------------------------------------------|
| **access_token**<br /> _required_  | The access token for the authenticated user. |

###### BODY
| Key                            | Value                                                                                                                      |
|--------------------------------|-------------------------------------------|
| **favoriteID**<br /> _required_     | New **string** value for the favorite's id.


###### Example Request:
```
POST http://146.185.190.181:49100/users/507f191e810c19729de860ea/favorite?access_token=<access_token>
Content-Type: application/json
{
	"favoriteID" : "810c19725071e9de860eaf19" 
}
```

###### Example Response
```
HTTP/1.1 201 Created
Location: http://146.185.190.181:49100:49100/users/507f191e810c19729de860ea/favorites/e860e810c19725f19071e9da
{	
	"favorite": 
	{	
		"_id":"53b01f5807384c0100a94271",
		"user":"53b01db6c0c4c601006445ea",
		"favorite":"This is the message.",
		"createdDate":"2014-06-29T14:14:09.368Z"
	}
}
```

###### CURL
```
 curl -i -X POST -H "Content-type: application/json" -d '{"favoriteID":"This is the message."}' 'http://146.185.190.181:49100/users/507f191e810c19729de860ea/favorite?access_token=<access_token>'
```

###### ERROR RESPONSES
| Code               | Description                                          |
|--------------------|-------------------------------|
| `400 BAD REQUEST`  | The request body is malformed.                       |
| `401 UNAUTHORIZED` | Authentication credentials are required to access the resource.                    |
| `409 CONFLICT`	 | A favorite with the provided favoriteID already exists.
| `500 INTERNAL SERVER ERROR` | Internal Server error.

---
#### <a id="favorites_get_multiple"></a> Get multiple favorites
This REST endpoint is private

###### Parameters
| Key                        | Value                                       |
|----------------------------|---------------------------------------------|
| **access_token**<br /> _required_  | The access token for the authenticated user. |

###### URI
```
GET http://146.185.190.181:49100/users/:userid/favorites
```

###### Example Request
```
GET http://146.185.190.181:49100/users/507f191e810c19729de860ea/favorites?access_token=<access_token>
```

###### Example Response
```
HTTP/1.1 200 OK
Content-Type: application/json; charset=UTF-8
{
	"favorites": 
	[   
		{
		    "_id": "52af48bb186a1e0200000006",
		    "favorite": "8bb1f46a1e0200006800052a",		  
		},
		{...}
	]
}
```

###### CURL
```
curl -i -X GET 'http://146.185.190.181:49100/users/507f191e810c19729de860ea/favorites?access_token=<access_token>'
```

###### ERROR RESPONSES
| Code               | Description                                                                        |
|--------------------|------------------------------------------------------------------------------------|
| `400 BAD REQUEST`  | The URL parameter is malformed.  
| `401 UNAUTHORIZED` | Authentication credentials are required to access the resource.                    |
| `404 NOT FOUND`    | No favorites could be found.                                   |
| `500 INTERNAL SERVER ERROR` | Internal Server error.

---