import os
import logging
import time
import json
import base64
import boto3

from datetime import datetime

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding

client = boto3.client('ssm')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

param = client.get_parameter(
  Name=os.environ['CLOUDFRONT_PK_PATH'],
  WithDecryption=True
)

private_key = serialization.load_pem_private_key(
  data=param['Parameter']['Value'].encode(),
  password=None,
  backend=default_backend()
)

logger.info('Retrieved private key from parameter store')


def aws_base64_encode(data):
  return base64.b64encode(data).replace(b'+', b'-').replace(b'=', b'_').replace(b'/', b'~')

def aws_base64_decode(data):
  return base64.b64decode(data.replace(b'-', b'+').replace(b'_', b'=').replace(b'~', b'/'))

def rsa_signer(private_key, message):
  return private_key.sign(message, padding.PKCS1v15(), hashes.SHA1())

def make_policy(resource, expire_date):
  policy = {
    'Statement': [{
      'Resource': resource,
      'Condition': {
        'DateLessThan': {
          'AWS:EpochTime': expire_date
        }
      }
    }]
  }
  return json.dumps(policy).replace(" ", "")

def generate_signed_cookie(policy, expire_date):
  policy = policy.encode('utf8')
  policy_b64 = aws_base64_encode(policy)

  signature = rsa_signer(private_key, policy)
  signature_b64 = aws_base64_encode(signature)

  return {
    'Policy'    : policy_b64.decode("utf-8"),
    'Signature' : signature_b64.decode("utf-8"),
    'Key'       : os.environ['KEY_ID'],
    'Expiration': expire_date
  }

def epoch_offset_from_now(offset_sec):
  now = datetime.now()
  epoch_offset = int(time.mktime(now.timetuple()))
  epoch_offset += offset_sec
  return epoch_offset

def generate_expiring_signed_cookie(resource, expire_date):
  policy = make_policy(resource, expire_date)
  signed_cookie = generate_signed_cookie(policy, expire_date)
  logger.info('Successfully generated signed cookies')
  return signed_cookie
