const jwt = require('jsonwebtoken');
const cf = require('aws-cloudfront-sign')
const fs = require('fs')
const ssm = new (require('aws-sdk/clients/ssm'))()

const errorUnexpected = new Error('Unexpected error')
const errorUnauthorized = new Error('Unauthorized')

exports.lambdaHandler = async (event) => {
    try {
        cookieDomain = getCookieDomain(event);
        expiration = getExpirationFromToken(event);
        cookies = await buildCookie(cookieDomain, expiration * 1000);
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": cookieDomain,
                "Access-Control-Allow-Methods": "GET, OPTIONS"
            },
            "body": JSON.stringify(cookies)
        }
    }
    catch (err) {
        console.log(err);
        return {
            "statusCode": 401,
            "headers": {
                "Access-Control-Allow-Origin": cookieDomain,
                "Access-Control-Allow-Methods": "GET, OPTIONS"
            },
            "body": err.message
        }
    }
}

function keysToLowercase(obj) {
    Object.fromEntries = arr => Object.assign({}, ...Array.from(arr, ([k, v]) => ({ [k]: v })));

    entries = Object.entries(obj).map(([k, v]) => [k.toLowerCase(), v]);
    result = Object.fromEntries(entries);
    return result;
}

function getCookieDomain(event) {
    headers = keysToLowercase(event.headers);
    if (!('origin' in headers)) {
        console.log('origin header missing');
        throw errorUnexpected;
    }
    return headers['origin'];
}

function getExpirationFromToken(event) {
    parameters = keysToLowercase(event.queryStringParameters);
    if (!('id_token' in parameters)) {
        console.log('id_token paramter missing');
        throw errorUnauthorized;
    }
    token = parameters['id_token'];

    try {
        decoded = jwt.verify(token, process.env.AUTH0_PUB_KEY);
    }
    catch (err) {
        console.log(err);
        throw errorUnauthorized;
    }

    if (!decoded.exp) {
        console.log('expiration not available in token');
        throw errorUnauthorized;
    }

    return decoded.exp
}

async function getSigningKey() {
    var params = {
        Name: process.env.PRIVATE_KEY_PARAM_NAME,
        WithDecryption: true
    };
    request = await ssm.getParameter(params).promise()
    return request.Parameter.Value
}

async function buildCookie(cookieDomain, expiration) {
    try {
        var options = { expireTime: expiration, keypairId: process.env.KEY_PAIR_ID, privateKeyString: await getSigningKey() }
        return cf.getSignedCookies(cookieDomain + '/*', options)
    }
    catch (err) {
        console.log(err)
        throw errorUnexpected
    }
}
