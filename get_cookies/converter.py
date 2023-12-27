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

    if expire_date < time.gmtime() + (60 * 60):
        logger.info('Token is short-lived, setting expiration to a week')
        expire_date = time.gmtime() + (60 * 60 * 24 * 7)

    return signer.generate_expiring_signed_cookie(resource=resource, expire_date=expire_date)
