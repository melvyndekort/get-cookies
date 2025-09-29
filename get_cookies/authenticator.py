import json
import logging
import os

import jwt
import requests
import validators

logger = logging.getLogger()
logger.setLevel(logging.INFO)

public_keys = {}
for jwks_uri in os.environ['JWKS_LIST'].split(","):
    if not validators.url(jwks_uri):
        logger.error(f'Invalid JWKS URI: {jwks_uri}')
        continue
    else:
        jwks = requests.get(jwks_uri, timeout=5).json()

    for jwk in jwks['keys']:
        kid = jwk['kid']
        logger.info(f'Found JWK for kid: {kid} in JWKS: {jwks_uri}')
        public_keys[kid] = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

audience_list = os.environ['CLIENT_ID_LIST'].split(',')


def get_expiration(token):
    """
    Extract and validate JWT token expiration.
    
    Args:
        token: JWT token string
        
    Returns:
        int: Token expiration time in milliseconds
    """
    public_key = get_public_key(token)

    options = {
        "require": ["email"]
    }

    decoded = jwt.decode(token,
                         key=public_key,
                         audience=audience_list,
                         algorithms=["RS256"],
                         options=options)

    logger.info(f'Successfully decoded token from user: {decoded["email"]}')
    return decoded['exp'] * 1000


def get_public_key(token):
    """
    Retrieve public key for JWT token verification.
    
    Args:
        token: JWT token string
        
    Returns:
        RSAPublicKey or None: Public key for token verification
    """
    kid = jwt.get_unverified_header(token)['kid']
    if kid in public_keys:
        logger.info(f'Found matching public key with id: {kid}')
        return public_keys[kid]
    else:
        logger.info('No matching public key found')
        return None
