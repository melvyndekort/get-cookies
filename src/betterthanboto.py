from boto.cloudfront.distribution import Distribution
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import base64

class BetterThanBoto(Distribution):

  def sign_rsa(self, message):
    private_key = serialization.load_pem_private_key(self.keyfile, password=None, backend=default_backend())
    signature = private_key.sign(data=message.encode('utf-8'),
                                 padding=padding.PKCS1v15(),
                                 algorithm=hashes.SHA1())
    return signature

  def _sign_string(self, message, private_key_string=None):
    self.keyfile = private_key_string.encode('utf-8')
    return self.sign_rsa(message)

  @staticmethod
  def _url_base64_encode(msg):
    msg_base64 = base64.b64encode(msg).decode('utf-8')
    msg_base64 = msg_base64.replace('+', '-')
    msg_base64 = msg_base64.replace('=', '_')
    msg_base64 = msg_base64.replace('/', '~')
    return msg_base64

  def generate_signature(self, policy, private_key_string=None):
    signature = self._sign_string(policy, private_key_string)
    encoded_signature = self._url_base64_encode(signature)
    return encoded_signature

  def create_signed_cookies(self, url, private_key_string=None, keypair_id=None, expires_at=20):
    policy = self._custom_policy(
      url,
      expires_at
    )

    encoded_policy = self._url_base64_encode(policy.encode('utf-8'))

    signature = self.generate_signature(
      policy, private_key_string=private_key_string
    )

    cookies = {
      "Policy": encoded_policy,
      "Signature": signature,
      "Key": keypair_id,
      "Expiration": expires_at
    }

    return cookies
