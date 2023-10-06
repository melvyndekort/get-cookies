import pytest
import time
import os
import json
import jwt
import base64
import requests

from cryptography.hazmat.primitives.serialization import load_pem_public_key

os.environ['JWKS_LIST'] = ''
from get_cookies import authenticator

##
# Fixtures
##
@pytest.fixture
def non_matching_jwks():
  jwks = {
    "keys": [
      {
        "kty": "RSA",
        "n": "foo",
        "e": "FOO",
        "kid": "foo"
      }
    ]
  }
  return json.dumps(jwks)

@pytest.fixture
def matching_jwks():
  jwks = {
    "keys": [
      {
        "kty": "RSA",
        "n": "u1SU1LfVLPHCozMxH2Mo4lgOEePzNm0tRgeLezV6ffAt0gunVTLw7onLRnrq0_IzW7yWR7QkrmBL7jTKEn5u-qKhbwKfBstIs-bMY2Zkp18gnTxKLxoS2tFczGkPLPgizskuemMghRniWaoLcyehkd3qqGElvW_VDL5AaWTg0nLVkjRo9z-40RQzuVaE8AkAFmxZzow3x-VJYKdjykkJ0iT9wCS0DRTXu269V264Vf_3jvredZiKRkgwlL9xNAwxXFg0x_XFw005UWVRIkdgcKWTjpBP2dPwVZ4WWC-9aGVd-Gyn1o0CLelf4rEjGoXbAAEgAqeGUxrcIlbjXfbcmw",
        "e": "AQAB",
        "kid": "correct"
      }
    ]
  }
  return json.dumps(jwks)

#def test_get_public_key_success_single(monkeypatch, der, matching_jwks, valid_token):
#  #requests_mock.get('http://matching', text=matching_jwks)
#
#  monkeypatch.setattr(authenticator, 'public_keys', {})
#
#  key = authenticator.get_public_key(valid_token)
#  expected = serialization.load_der_public_key(der)
#  assert key == expected
#
#def test_get_public_key_success_multi_1(requests_mock, der, non_matching_jwks, matching_jwks, valid_token):
#  requests_mock.get('http://non-matching', text=non_matching_jwks)
#  requests_mock.get('http://matching', text=matching_jwks)
#
#  os.environ['JWKS_LIST'] = 'http://non-matching,http://matching'
#  from get_cookies import authenticator
#  key = authenticator.get_public_key(valid_token)
#  expected = serialization.load_der_public_key(der)
#  assert key == expected
#
#def test_get_public_key_success_multi_2(requests_mock, der, non_matching_jwks, matching_jwks, valid_token):
#  requests_mock.get('http://matching', text=matching_jwks)
#  requests_mock.get('http://non-matching', text=non_matching_jwks)
#
#  os.environ['JWKS_LIST'] = 'http://matching,http://non-matching'
#  from get_cookies import authenticator
#  key = authenticator.get_public_key(valid_token)
#  expected = serialization.load_der_public_key(der)
#  assert key == expected
#
#def test_get_public_key_no_match(requests_mock, der, non_matching_jwks, valid_token):
#  requests_mock.get('http://non-matching', text=non_matching_jwks)
#
#  os.environ['JWKS_LIST'] = 'http://non-matching'
#  from get_cookies import authenticator
#  key = authenticator.get_public_key(valid_token)
#  assert key == None
