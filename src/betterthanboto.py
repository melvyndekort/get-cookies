from boto.cloudfront.distribution import Distribution
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import base64

class BetterThanBoto(Distribution):

    def sign_rsa(self, message):
        private_key = serialization.load_pem_private_key(self.keyfile, password=None,
                            backend=default_backend())
        signature = private_key.sign(data=message.encode('utf-8'),
                                     padding=padding.PKCS1v15(),
                                     algorithm=hashes.SHA1())
        return signature

    def _sign_string(self, message, private_key_string=None):
        self.keyfile = private_key_string.encode('utf-8')
        return self.sign_rsa(message)

    @staticmethod
    def _url_base64_encode(msg):
        """
        Base64 encodes a string using the URL-safe characters specified by
        Amazon.
        """
        msg_base64 = base64.b64encode(msg).decode('utf-8')
        msg_base64 = msg_base64.replace('+', '-')
        msg_base64 = msg_base64.replace('=', '_')
        msg_base64 = msg_base64.replace('/', '~')
        return msg_base64

    def generate_signature(self, policy, private_key_string=None):
        """
        :param policy: no-whitespace json str (NOT encoded yet)
        :param private_key_file: your .pem file with which to sign the policy
        :return: encoded signature for use in cookie
        """
        # Distribution._create_signing_params()
        signature = self._sign_string(policy, private_key_string)

        # now base64 encode the signature & make URL safe
        encoded_signature = self._url_base64_encode(signature)

        return encoded_signature

    def create_signed_cookies(self, url, private_key_string=None, keypair_id=None,
            expires_at=20, secure=True):
        """
        generate the Cloudfront download distirbution signed cookies
        :param resource: The object or path of resource.
                         Examples: 'dir/object.mp4', 'dir/*', '*'
        :param private_key_file: Path to the private key file (pem encoded)
        :param key_pair_id: ID of the keypair used to sign the cookie
        :param expire_minutes:  The number of minutes until expiration
        :param secure: use https or http protocol for Cloudfront URL - update
                       to match your distribution settings.
        :return: Cookies to be set
        """

        # generate no-whitespace json policy,
        # then base64 encode & make url safe
        policy = self._custom_policy(
            url,
            expires_at
        )
        
        encoded_policy = self._url_base64_encode(policy.encode('utf-8'))

        # assemble the 3 Cloudfront cookies
        signature = self.generate_signature(
            policy, private_key_string=private_key_string
        )
        cookies = {
            "CloudFront-Policy": encoded_policy,
            "CloudFront-Signature": signature,
            "CloudFront-Key-Pair-Id": keypair_id
        }
        return cookies
