import os
import jwt
import requests
import json
import boto3
import datetime

from signed_cookie_generator import CookieGen

def lambda_handler(event, context):
  try:
    token = event['queryStringParameters']['id_token']

    public_key = get_public_key(token)
    decoded = jwt.decode(token,
                         key=public_key,
                         audience=os.environ['CLIENT_ID'],
                         algorithms=["RS256"])

    expire_date = decoded['exp'] * 1000

    resource = event['headers']['origin'] + "/*"

    cg = CookieGen()
    cookies = cg.generate_expiring_signed_cookie(resource=resource,
                                                 expire_date=expire_date,
                                                 key_id=os.environ['KEY_ID'])

    resp = {
      "statusCode": 200,
      "body": json.dumps(cookies)
    }
    return resp

  except Exception as e:
    print(str(e))
    raise Exception('Internal server error')

def get_public_key(token):
    resp = requests.get(os.environ['JWKS_URI'])
    jwks = resp.json()

    public_keys = {}
    for jwk in jwks['keys']:
        kid = jwk['kid']
        public_keys[kid] = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

    kid = jwt.get_unverified_header(token)['kid']
    return public_keys[kid]
