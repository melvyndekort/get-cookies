const jwt = require('jsonwebtoken');
const cf = require('aws-cloudfront-sign')
const fs = require('fs')
const ssm = new (require('aws-sdk/clients/ssm'))()

const UnexpectedError = require('./UnexpectedError.js')
const UnauthorizedError = require('./UnauthorizedError.js')

exports.lambdaHandler = async (event) => {
    try {
        cookieDomain = getCookieDomain(event);
        expiration = getExpirationFromToken(event);
        cookies = await buildCookie(cookieDomain, expiration * 1000);

        body = {
            'Expiration': expiration,
            'Policy': cookies['CloudFront-Policy'],
            'Signature': cookies['CloudFront-Signature'],
            'Key': process.env.KEY_PAIR_ID
        }

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': cookieDomain,
                'Access-Control-Allow-Methods': 'GET, OPTIONS'
            },
            'body': JSON.stringify(body)
        }
    }
    catch (err) {
        console.log(err);
        return {
            'statusCode': err.status,
            'headers': {
                'Access-Control-Allow-Origin': cookieDomain,
                'Access-Control-Allow-Methods': 'GET, OPTIONS'
            },
            'body': err.message
        }
    }
}

function keysToLowerCase(obj) {
    Object.fromEntries = arr => Object.assign({}, ...Array.from(arr, ([k, v]) => ({ [k]: v })));

    entries = Object.entries(obj).map(([k, v]) => [k.toLowerCase(), v]);
    return Object.fromEntries(entries);
}

function getCookieDomain(event) {
    headers = keysToLowerCase(event.headers);
    if (!('origin' in headers)) {
        console.log('origin header missing');
        throw new UnexpectedError();
    }
    return headers['origin'];
}

function getExpirationFromToken(event) {
    parameters = keysToLowerCase(event.queryStringParameters);
    if (!('id_token' in parameters)) {
        console.log('id_token parameter missing');
        throw new UnauthorizedError();
    }
    token = parameters['id_token'];

    try {
        decoded = jwt.verify(token, process.env.AUTH0_PUB_KEY);
    }
    catch (err) {
        console.log(err);
        throw new UnauthorizedError();
    }

    if (!decoded.exp) {
        console.log('expiration not available in token');
        throw new UnauthorizedError();
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
        throw new UnexpectedError()
    }
}
