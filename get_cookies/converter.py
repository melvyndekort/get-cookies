"""Turns a validated JWT into a signed-cookie policy for the client's origin."""

import logging
import time

from get_cookies import authenticator
from get_cookies import signer

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_cookies(token, origin):
    """Return signed cookie fields scoping access to origin, expiring with the token."""
    expire_date = authenticator.get_expiration(token)
    logger.info('Token will expire at: %s', expire_date)

    resource = origin + "/*"
    logger.info('Client came from: %s', resource)

    current_time_ms = round(time.time() * 1000)
    one_hour_ms = 60 * 60 * 1000
    one_week_ms = 7 * 24 * 60 * 60 * 1000

    if expire_date < current_time_ms + one_hour_ms:
        expire_date = current_time_ms + one_week_ms
        logger.info('Token is short-lived, setting expiration to 7 days: %s', expire_date)

    return signer.generate_expiring_signed_cookie(resource=resource, expire_date=expire_date)
