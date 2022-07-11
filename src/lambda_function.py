import os
import logging
import jwt
import requests
import json
import boto3
import datetime

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

from signed_cookie_generator import CookieGen

logging.basicConfig(level=logging.INFO)
patch_all()

def lambda_handler(event, context):
  try:
    token = event['queryStringParameters']['id_token']

    public_key = get_public_key(token)
    logging.info("Found public key: %s", public_key)

    decoded = jwt.decode(token,
                         key=public_key,
                         audience=os.environ['CLIENT_ID'],
                         algorithms=["RS256"])

    expire_date = decoded['exp'] * 1000
    logging.info("Token will expire at: %s", expire_date)

    resource = event['headers']['origin'] + "/*"
    logging.info("Client came from: %s", resource)

    cg = CookieGen()
    cookies = cg.generate_expiring_signed_cookie(resource=resource,
                                                 expire_date=expire_date,
                                                 key_id=os.environ['KEY_ID'])
    logging.info("Successfully generated signed cookies")

    resp = {
      'statusCode': 200,
      'headers': {
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Origin': event['headers']['origin'],
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
      },
      'body': json.dumps(cookies)
    }
    return resp

  except Exception as e:
    logging.error(str(e))
    resp = {
      'statusCode': 401,
      'headers': {
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Origin': event['headers']['origin'],
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
      },
      'body': 'Unauthorized'
    }
    return resp

def get_public_key(token):
    resp = requests.get(os.environ['JWKS_URI'])
    jwks = resp.json()

    public_keys = {}
    for jwk in jwks['keys']:
        kid = jwk['kid']
        public_keys[kid] = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

    kid = jwt.get_unverified_header(token)['kid']
    return public_keys[kid]
