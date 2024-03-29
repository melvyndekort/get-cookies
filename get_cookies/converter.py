import logging
import time

from get_cookies import authenticator
from get_cookies import signer

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_cookies(token, origin):
    expire_date = authenticator.get_expiration(token)
    logger.info(f'Token will expire at: {expire_date}')

    resource = origin + "/*"
    logger.info(f'Client came from: {resource}')

    time_ms = round(time.time() * 1000)
    if expire_date < time_ms + (1000 * 60 * 60):
        expire_date = time_ms + (1000 * 60 * 60 * 24 * 7)
        logger.info('Token is short-lived, setting expiration to 7 days: %s', expire_date)

    return signer.generate_expiring_signed_cookie(resource=resource, expire_date=expire_date)
