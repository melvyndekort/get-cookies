import os
import jwt
import requests
import json
import boto3

from betterthanboto import BetterThanBoto

def lambda_handler(event, context):
  try:
    token = event['queryStringParameters']['id_token']

    public_key = get_public_key(token)
    decoded = jwt.decode(token,
                         key=public_key,
                         audience=os.environ['CLIENT_ID'],
                         algorithms=["RS256"])

    cf = BetterThanBoto()
    cookies = cf.create_signed_cookies(url='/',
                                       keypair_id=os.environ['KEY_ID'],
                                       expires_at=decoded['exp'] * 1000,
                                       private_key_string=get_signing_key())

    reply = {
      "statusCode": 200,
      "body": json.dumps(cookies)
    }
    print(reply)
    return reply

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


def get_signing_key():
  ssm_client = boto3.client('ssm')

  param = ssm_client.get_parameter(
      Name=os.environ['CLOUDFRONT_PK_PATH'],
      WithDecryption=True
  )

  return param['Parameter']['Value']
