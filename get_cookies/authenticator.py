"""JWT authentication: fetches JWKS public keys at import time, verifies tokens."""

import json
import logging
import os
import re

import jwt
import requests
import validators

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# JWT token format validation
JWT_PATTERN = re.compile(r'^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$')

def _validate_jwt_format(token):
    """Validate JWT token format before processing."""
    if not token or not isinstance(token, str):
        return False
    if len(token) > 8192:  # Reasonable JWT size limit
        return False
    return JWT_PATTERN.match(token) is not None

public_keys = {}
for jwks_uri in os.environ['JWKS_LIST'].split(","):
    jwks_uri = jwks_uri.strip()
    if not validators.url(jwks_uri):
        logger.error('Invalid JWKS URI: %s', jwks_uri)
        continue

    try:
        # Secure JWKS request with strict timeout and size limits
        response = requests.get(
            jwks_uri,
            timeout=5,
            headers={'User-Agent': 'get-cookies/1.0'},
            stream=True
        )
        response.raise_for_status()

        # Limit response size to prevent DoS
        content_length = response.headers.get('content-length')
        if content_length and int(content_length) > 1024 * 1024:  # 1MB limit
            logger.error('JWKS response too large from %s', jwks_uri)
            continue

        jwks = response.json()

        if not isinstance(jwks, dict) or 'keys' not in jwks:
            logger.error('Invalid JWKS format from %s', jwks_uri)
            continue

    except (requests.RequestException, ValueError, KeyError) as e:
        logger.error('Failed to fetch JWKS from %s: %s', jwks_uri, e)
        continue

    for jwk in jwks['keys']:
        try:
            jwk_kid = jwk['kid']
            if not jwk_kid or not isinstance(jwk_kid, str):
                logger.warning('Invalid kid in JWK from %s', jwks_uri)
                continue

            logger.info('Found JWK for kid: %s in JWKS: %s', jwk_kid, jwks_uri)
            public_keys[jwk_kid] = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
        except (KeyError, ValueError) as e:
            logger.warning('Failed to process JWK from %s: %s', jwks_uri, e)
            continue

audience_list = os.environ['CLIENT_ID_LIST'].split(',')


def get_expiration(token):
    """
    Extract and validate JWT token expiration.

    Args:
        token: JWT token string

    Returns:
        int: Token expiration time in milliseconds
    """
    if not _validate_jwt_format(token):
        raise ValueError("Invalid JWT token format")

    public_key = get_public_key(token)
    if not public_key:
        raise ValueError("No valid public key found for token")

    options = {
        "require": ["email", "exp", "aud"]
    }

    decoded = jwt.decode(token,
                         key=public_key,
                         audience=audience_list,
                         algorithms=["RS256"],
                         options=options)

    logger.info('Successfully decoded token from user: %s', decoded["email"])
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
        logger.info('Found matching public key with id: %s', kid)
        return public_keys[kid]
    logger.info('No matching public key found')
    return None
