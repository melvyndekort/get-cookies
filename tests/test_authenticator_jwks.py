import pytest
import os
import requests
import importlib
import json

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

@pytest.fixture(scope="function")
def init_authenticator_one(requests_mock, matching_jwks):
  requests_mock.get('https://example.com/matching', text=matching_jwks)

  os.environ['JWKS_LIST'] = 'https://example.com/matching'
  return importlib.reload(authenticator)

@pytest.fixture(scope="function")
def init_authenticator_two(requests_mock, matching_jwks, non_matching_jwks):
  requests_mock.get('https://example.com/matching', text=matching_jwks)
  requests_mock.get('https://example.com/non-matching', text=non_matching_jwks)

  os.environ['JWKS_LIST'] = 'https://example.com/matching,https://example.com/non-matching'
  return importlib.reload(authenticator)


##
# Tests
##
def test_initialize_authenticator_empty():
  assert len(authenticator.public_keys) == 0

def test_initialize_authenticator_one(init_authenticator_one):
  assert len(init_authenticator_one.public_keys) == 1

def test_initialize_authenticator_two(init_authenticator_two):
  assert len(init_authenticator_two.public_keys) == 2
