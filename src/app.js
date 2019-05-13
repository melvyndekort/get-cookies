const jwt = require('jsonwebtoken');
const cf = require('aws-cloudfront-sign')
const fs = require('fs')
const ssm = new (require('aws-sdk/clients/ssm'))()

const errorUnexpected = new Error('Unexpected error')
const errorUnauthorized = new Error('Unauthorized')

exports.lambdaHandler = async (event) => {
    cookieDomain = getCookieDomain(event);
    expiration = getExpirationFromToken(event);
    cookies = await buildCookie(cookieDomain, expiration * 1000)
    return JSON.stringify(cookies)
}

function getCookieDomain(event) {
    if (!'origin' in event.headers) {
        console.log('origin header missing');
        throw errorUnexpected;
    }
    cookieDomain = event.headers['origin'];
}

function getExpirationFromToken(event) {
    if (!'id_token' in event.queryStringParameters) {
        console.log('id_token paramter missing');
        throw errorUnauthorized;
    }
    token = event.queryStringParameters['id_token'];

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
