import os
import logging
import jwt
import requests
import json

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_expiration(token):
  public_key = get_public_key(token)
  audience = os.environ['CLIENT_ID']

  decoded = jwt.decode(token,
                       key=public_key,
                       audience=audience,
                       algorithms=["RS256"])

  return decoded['exp'] * 1000

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
