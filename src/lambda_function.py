import os
import logging
import jwt
import requests
import json
import datetime

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

logger = logging.getLogger()
logger.setLevel(logging.INFO)

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
    logger.info(f'Token will expire at: {expire_date}')

    private_key = get_private_key()

    resource = event['headers']['origin'] + "/*"
    logger.info(f'Client came from: {resource}')

    cookieGen = CookieGen()
    cookies = cookieGen.generate_expiring_signed_cookie(private_key=private_key,
                                                        resource=resource,
                                                        expire_date=expire_date,
                                                        key_id=os.environ['KEY_ID'])

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
    logger.exception("Exception occurred")

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
  logger.info(f'Found public key with id: {kid}')

  return public_keys[kid]

def get_private_key():
  param_name = os.environ['CLOUDFRONT_PK_PATH']
  url = f'http://localhost:2773/systemsmanager/parameters/get?name={param_name}&withDecryption=true'
  headers = {'X-Aws-Parameters-Secrets-Token': os.environ['AWS_SESSION_TOKEN']}
  response = requests.get(url, headers=headers).json()

  private_key = serialization.load_pem_private_key(
    data=response['Parameter']['Value'].encode(),
    password=None,
    backend=default_backend()
  )

  logger.info('Retrieved private key from parameter store')

  return private_key
