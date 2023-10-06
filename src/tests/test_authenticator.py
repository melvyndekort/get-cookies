import pytest
import time
import os
import jwt

from cryptography.hazmat.primitives.serialization import load_pem_public_key

os.environ['JWKS_LIST'] = ''
from get_cookies import authenticator

##
# Fixtures
##
@pytest.fixture
def public_key():
  pubkey = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu1SU1LfVLPHCozMxH2Mo
4lgOEePzNm0tRgeLezV6ffAt0gunVTLw7onLRnrq0/IzW7yWR7QkrmBL7jTKEn5u
+qKhbwKfBstIs+bMY2Zkp18gnTxKLxoS2tFczGkPLPgizskuemMghRniWaoLcyeh
kd3qqGElvW/VDL5AaWTg0nLVkjRo9z+40RQzuVaE8AkAFmxZzow3x+VJYKdjykkJ
0iT9wCS0DRTXu269V264Vf/3jvredZiKRkgwlL9xNAwxXFg0x/XFw005UWVRIkdg
cKWTjpBP2dPwVZ4WWC+9aGVd+Gyn1o0CLelf4rEjGoXbAAEgAqeGUxrcIlbjXfbc
mwIDAQAB
-----END PUBLIC KEY-----
"""
  return load_pem_public_key(bytes(pubkey, 'utf-8'))

@pytest.fixture
def token_valid():
  # exp = 32503680000000
  return "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImNvcnJlY3QifQ.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiZW1haWwiOiJqLmRvZUBleGFtcGxlLmNvbSIsImFkbWluIjp0cnVlLCJpYXQiOjE1MTYyMzkwMjIsImF1ZCI6InB5dGVzdCIsImV4cCI6MzI1MDM2ODAwMDAwMDB9.BKxH3O0coFgT9JcghzcEwBSr0-56mlcn3OyqHdTpGqIW-j7oshlUhHfQorh929DrBfGoy1XyLO0xBL7Avydwlo_CYN8lGua0TZ5rRGbZrxMDWbErs_n4dh8qMkcUoHbJJR9wDIbOuBaQ3kWdjc1kWZwC9rPyMXWpDToy2PRs1cAWq2ZitGSEUNH-c453tZXKBoW9tlmWZmpP1YeNmHdUKcJMLYCVYNQHm-_fz4HoHgUnS5eS97_iXiGvpSjRcut3Wbynr7UmFx4hfM4986px589LKXlbzliR4YfRd3hSoXKSlWvyzF1UcsOWQWXo7cSBdSS-I6Lv6p7a-eMP4GUMVg"

@pytest.fixture
def token_expired():
  # exp = 946688400
  return "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImNvcnJlY3QifQ.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiZW1haWwiOiJqLmRvZUBleGFtcGxlLmNvbSIsImFkbWluIjp0cnVlLCJpYXQiOjE1MTYyMzkwMjIsImF1ZCI6InB5dGVzdCIsImV4cCI6OTQ2Njg4NDAwfQ.IKJ5bYuGMkzITjyHN89v4WDR5SZdL2hAPEUFM60xTs7s-S2E0zOje3Xl-zQZ64iu-hD3KWuWyzen0FRoOO9LyYP-y9Vbg2qyi4CJNuLXVstFZxAVVlHcNRBL3lU5-PB8-iKE8SLIEKTyIDzXy3H_ofyUe8pHNjw8xvEifVgIFZPh_nVcGoR4RCOk6EzfQWgg-ZpJC9zZqLo2LICgIG3orClcv_9Ni13ktCA49zTz_0zT9f5OMv9uPUO8CL-i1xQQ0oMrAQIREADUCYzpgv7X-GRPscvDKxyWRf0aivY6mJ7dy9F7IaJ8NPqQPJOJR6lnOrtqLAap8iVQNb0NXO44Vw"

@pytest.fixture
def token_missing_email():
  # exp = 32503680000000
  return "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImNvcnJlY3QifQ.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMiwiYXVkIjoicHl0ZXN0IiwiZXhwIjozMjUwMzY4MDAwMDAwMH0.X1mYD2Rot_jCE3-35xF-kMEjlQXunTCUcXzbKXOHhwOVASBy0d7HBC53qtBWT1-4BQ-9ZwKSEiG8YMSaJPdb2JsY9yAQkVQEK9xHu3Tqi0oI6u_V-nhNfpy6rLQ8mEWbVCXPPp5DWIiZv-fXRq8Uk6nA7MKqQ2ieDlMIKG7OyIeOgpqY5mSDtjaUHrEfpt-ZwOIppy15yuTOShLRGSKYylC6h2YkolqPMnuNxbIntxSrIDeEbsPzGfbYxR1tgub2-OO9-Z7xXdxogbqfH8e8FDjRykSCKQrSl1tykiJxFbg0e0Kmf_jicuh967wnjSvb0O5fMEmrHyrulwChX8uUgw"

@pytest.fixture
def public_key_available(monkeypatch, public_key):
  public_keys = {}
  public_keys['correct'] = public_key
  monkeypatch.setattr(authenticator, 'public_keys', public_keys)

##
# Tests
##
def test_get_public_key_success(monkeypatch, token_valid, public_key):
  public_keys = {}
  public_keys['foo'] = None
  public_keys['bar'] = 'foobar'
  public_keys['correct'] = public_key
  monkeypatch.setattr(authenticator, 'public_keys', public_keys)

  key = authenticator.get_public_key(token_valid)
  expected = public_key
  assert key == expected

def test_get_public_key_failure(monkeypatch, token_valid):
  public_keys = {}
  public_keys['foo'] = 'test'
  public_keys['bar'] = 'foobar'
  monkeypatch.setattr(authenticator, 'public_keys', public_keys)

  key = authenticator.get_public_key(token_valid)
  assert key == None

def test_get_expiration_success(public_key_available, token_valid):
  os.environ['CLIENT_ID'] = 'pytest'
  exp = authenticator.get_expiration(token_valid)
  assert exp > time.time()

def test_get_expiration_expired(public_key_available, token_expired):
  os.environ['CLIENT_ID'] = 'pytest'
  try:
    exp = authenticator.get_expiration(token_expired)
    assert False
  except jwt.exceptions.ExpiredSignatureError:
    assert True

def test_get_expiration_incorrect_audience(public_key_available, token_valid):
  os.environ['CLIENT_ID'] = 'fail'
  try:
    exp = authenticator.get_expiration(token_valid)
    assert False
  except jwt.exceptions.InvalidAudienceError:
    assert True

def test_get_expiration_missing_email_claim(public_key_available, token_missing_email):
  os.environ['CLIENT_ID'] = 'pytest'
  try:
    exp = authenticator.get_expiration(token_missing_email)
    assert False
  except jwt.exceptions.MissingRequiredClaimError:
    assert True
