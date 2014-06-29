/**
 *	holist-server > HTTPStatusCodes.js
 *	Copyright (c) 2014, Robert Weindl. All rights reserved.
 */

var HTTPStatusCode =
{
    // 1xx Informational
     'HTTPStatusCode100Continue' : 100,
     'HTTPStatusCode101SwitchingProtocols' : 101,

     // 2xx Successful
     'HTTPStatusCode200OK' : 200,
     'HTTPStatusCode201Created' : 201,
     'HTTPStatusCode202Accepted' : 202,
     'HTTPStatusCode203NonAuthoritativeInformation' : 203,
     'HTTPStatusCode204NoContent' : 204,
     'HTTPStatusCode205ResetContent' : 205,
     'HTTPStatusCode206PartialContent' : 206,

     // 3xx Redirection
     'HTTPStatusCode300MultipleChoices' : 300,
     'HTTPStatusCode301MovedPermanently' : 301,
     'HTTPStatusCode302Found' : 302,
     'HTTPStatusCode303SeeOther' : 303,
     'HTTPStatusCode304NotModified' : 304,
     'HTTPStatusCode305UseProxy' : 305,
     'HTTPStatusCode307TemporaryRedirect' : 307,

     // 4xx Client Error
     'HTTPStatusCode400BadRequest' : 400,
     'HTTPStatusCode401Unauthorized' : 401,
     'HTTPStatusCode402PaymentRequired' : 402,
     'HTTPStatusCode403Forbidden' : 403,
     'HTTPStatusCode404NotFound' : 404,
     'HTTPStatusCode405MethodNotAllowed' : 405,
     'HTTPStatusCode406NotAcceptable' : 406,
     'HTTPStatusCode407ProxyAuthenticationRequired' : 407,
     'HTTPStatusCode408RequestTimeout' : 408,
     'HTTPStatusCode409Conflict' : 409,
     'HTTPStatusCode410Gone' : 410,
     'HTTPStatusCode411LengthRequired' : 411,
     'HTTPStatusCode412PreconditionFailed' : 412,
     'HTTPStatusCode413RequestEntityTooLarge' : 413,
     'HTTPStatusCode414RequestURITooLong' : 414,
     'HTTPStatusCode415UnsupportedMediaType' : 415,
     'HTTPStatusCode416RequestedRangeNotSatisfiable' : 416,
     'HTTPStatusCode417ExpectationFailed' : 417,

     // 5xx Server Error
     'HTTPStatusCode500InternalServerError' : 500,
     'HTTPStatusCode501NotImplemented' : 501,
     'HTTPStatusCode502BadGateway' : 502,
     'HTTPStatusCode503ServiceUnavailable' : 503,
     'HTTPStatusCode504GatewayTimeout' : 504,
     'HTTPStatusCode505HTTPVersionNotSupported' : 505
};
module.exports = HTTPStatusCode;
