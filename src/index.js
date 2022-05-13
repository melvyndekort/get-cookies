import 'dotenv/config'
import jwt from 'jsonwebtoken';
import jwksClient from 'jwks-rsa';
import cf from 'aws-cloudfront-sign';
import { SSMClient, GetParameterCommand } from "@aws-sdk/client-ssm";

import UnexpectedError from './UnexpectedError.js';
import UnauthorizedError from './UnauthorizedError.js';

const ssmClient = new SSMClient();
const input = {
  Name: process.env.CLOUDFRONT_PK_PATH,
  WithDecryption: true
};
const command = new GetParameterCommand(input);
const parameter = await ssmClient.send(command);

const client = jwksClient({
  cache: true,
  cacheMaxEntries: 5,
  cacheMaxAge: 600000,
  jwksUri: process.env.JWKS_URI,
  timeout: 5000
});

export async function handler(event) {
  try {
    const cookieDomain = getCookieDomain(event);
    const token = getToken(event);
    const expiration = await getExpirationFromToken(token);
    const cookies = await buildCookie(cookieDomain, expiration * 1000);

    const body = {
      'Expiration': expiration,
      'Policy': cookies['CloudFront-Policy'],
      'Signature': cookies['CloudFront-Signature'],
      'Key': process.env.KEY_ID
    };

    const response = {
      'statusCode': 200,
      'body': JSON.stringify(body)
    };
    return response;
  } catch (err) {
    console.log(err);
    throw err;
  }
}

function getkid(token) {
  const decoded = jwt.decode(token, {complete: true});
  const kid = decoded.header.kid;
  console.log("Found KID in token: %s", kid);
  return kid;
}

async function getPublicKey(kid) {
  const key = await client.getSigningKey(kid);
  console.log("Found public key for KID '%s' in JWKS", key.kid);
  return key.getPublicKey();
}

async function verifyToken(token) {
  try {
    const kid = getkid(token);
    const publicKey = await getPublicKey(kid);
    return jwt.verify(token, publicKey, { algorithms: ['RS256'], audience: process.env.CLIENT_ID });
  } catch (err) {
    console.log(err);
    throw new UnauthorizedError();
  }
}

function getCookieDomain(event) {
  if (!('origin' in event.headers)) {
    console.log('origin header missing');
    throw new UnexpectedError();
  }
  const origin = event.headers['origin'];
  console.log("Found origin in headers: %s", origin);
  return origin;
}

async function getExpirationFromToken(token) {
  const decoded = await verifyToken(token);
  if (!decoded.exp) {
    console.log('expiration not available in token');
    throw new UnauthorizedError();
  }
  console.log("Found expiration in token: %s", decoded.exp);
  return decoded.exp;
}

function getToken(event) {
  if (!('id_token' in event.queryStringParameters)) {
    console.log('id_token parameter missing');
    throw new UnauthorizedError();
  }
  return event.queryStringParameters['id_token'];
}

async function buildCookie(cookieDomain, expiration) {
  try {
    var options = {
      expireTime: expiration,
      keypairId: process.env.KEY_ID,
      privateKeyString: parameter.Parameter.Value
    }
    return cf.getSignedCookies(cookieDomain + '/*', options);
  } catch (err) {
    console.log(err);
    throw new UnexpectedError();
  }
}
