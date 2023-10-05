import logging
import authenticator
import signer

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_cookies(token, origin):
  expire_date = authenticator.get_expiration(token)
  logger.info(f'Token will expire at: {expire_date}')

  resource = origin + "/*"
  logger.info(f'Client came from: {resource}')

  return signer.generate_expiring_signed_cookie(private_key=private_key,
                                                resource=resource,
                                                expire_date=expire_date)
