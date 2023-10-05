import pytest
import os
import json
import jwt
import base64
import requests

from cryptography.hazmat.primitives import serialization
from get_cookies import authenticator

@pytest.fixture
def der():
  key_data = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu1SU1LfVLPHCozMxH2Mo4lgOEePzNm0tRgeLezV6ffAt0gunVTLw7onLRnrq0/IzW7yWR7QkrmBL7jTKEn5u+qKhbwKfBstIs+bMY2Zkp18gnTxKLxoS2tFczGkPLPgizskuemMghRniWaoLcyehkd3qqGElvW/VDL5AaWTg0nLVkjRo9z+40RQzuVaE8AkAFmxZzow3x+VJYKdjykkJ0iT9wCS0DRTXu269V264Vf/3jvredZiKRkgwlL9xNAwxXFg0x/XFw005UWVRIkdgcKWTjpBP2dPwVZ4WWC+9aGVd+Gyn1o0CLelf4rEjGoXbAAEgAqeGUxrcIlbjXfbcmwIDAQAB"
  return base64.b64decode(key_data)

@pytest.fixture
def jwk():
  return {
    "kty": "RSA",
    "n": "u1SU1LfVLPHCozMxH2Mo4lgOEePzNm0tRgeLezV6ffAt0gunVTLw7onLRnrq0_IzW7yWR7QkrmBL7jTKEn5u-qKhbwKfBstIs-bMY2Zkp18gnTxKLxoS2tFczGkPLPgizskuemMghRniWaoLcyehkd3qqGElvW_VDL5AaWTg0nLVkjRo9z-40RQzuVaE8AkAFmxZzow3x-VJYKdjykkJ0iT9wCS0DRTXu269V264Vf_3jvredZiKRkgwlL9xNAwxXFg0x_XFw005UWVRIkdgcKWTjpBP2dPwVZ4WWC-9aGVd-Gyn1o0CLelf4rEjGoXbAAEgAqeGUxrcIlbjXfbcmw",
    "e": "AQAB",
    "kid": "test"
  }

@pytest.fixture
def jwks_response(jwk):
  jwks = { 
    "keys": [
      jwk
    ]
  }
  return json.dumps(jwks)

@pytest.fixture
def valid_token():
  return "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InRlc3QifQ.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMiwiYXVkIjoicHl0ZXN0IiwiZXhwIjozMjUwMzY4MDAwMH0.lL4x4vqnn0300EImOkc8VmGShCrjv8usEYNw13J0jbptBzEO6_Bol7xoZF-9AijO6VD7VSiEA3003W81SyyioBzHzB4etyOedWoBl6IFJRmFl7tbDYsXt5iT-GyLlTDlgIUd6imA7HQWp72s-KdVlOyZuydxIpnlIB6eLH-yCX0aa_w4FoeFnko1jQ6DLvfkCQ4S7POEx4-b5ZZ7BeIPeYR5p1PmDZzNIIEY15RqsiEvl1TXgQCE5My465PJF5Qb-1c6em8XXzMN0mziQROvTFpCa7buLBKQybFA8UsEvCYZVMDevqHAKnXXqrRDUXOgk22a5e6-X15Em-bueayIqA"

@pytest.fixture
def expired_token():
  return "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InRlc3QifQ.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMiwiYXVkIjoicHl0ZXN0IiwiZXhwIjo5NDY2ODQ4MDB9.oWF4xTrmBUCVaBa9aBcP-D904lki2T_qAOtn_CtgQiFCi1eZ8ff6CiCwhp4gBzjCycaZGvS_m-t00qnh-ig_DMqOTHYXLQo0TXkZa3jpQskznuUY9SM08ws5f8rFS4MLZ95aQnPbuWNYywUbEUPFgCXkbhgMnovDI_oAcJhBfY_Fmq3qF12DWUpSKmxSplC5UcbPbV2JrtyDWWAxfkbgnB5MoAIBmXksRgJbKeSSjQuJPp3E5iKPZZQJDHesxsn_2KfgrHoXrrcaMEAdIps-C2faxv3o0RK4vWgb_rJ6KWpfpPOpl8w8mNnCh7UFjm001hu0Ez17CEZktC9NQZe5vg"


def test_get_public_key_success(requests_mock, der, jwks_response, valid_token):
  os.environ['JWKS_URI'] = 'http://localhost'

  requests_mock.get('http://localhost', text=jwks_response)

  key = authenticator.get_public_key(valid_token)
  expected = serialization.load_der_public_key(der)
  assert key == expected

def test_get_public_key_jwks_empty(requests_mock, valid_token):
  os.environ['JWKS_URI'] = 'http://localhost'

  requests_mock.get('http://localhost', text='')

  try:
    authenticator.get_public_key(valid_token)
    assert False
  except requests.exceptions.JSONDecodeError:
    assert True

def test_get_expiration_success(requests_mock, jwks_response, valid_token):
  os.environ['JWKS_URI'] = 'http://localhost'
  os.environ['CLIENT_ID'] = 'pytest'

  requests_mock.get('http://localhost', text=jwks_response)

  exp = authenticator.get_expiration(valid_token)
  assert exp == 32503680000000

def test_get_expiration_expired(requests_mock, jwks_response, expired_token):
  os.environ['JWKS_URI'] = 'http://localhost'
  os.environ['CLIENT_ID'] = 'pytest'

  requests_mock.get('http://localhost', text=jwks_response)

  try:
    exp = authenticator.get_expiration(expired_token)
    assert False
  except jwt.exceptions.ExpiredSignatureError:
    assert True
