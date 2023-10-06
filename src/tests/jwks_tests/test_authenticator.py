import pytest
import os
import requests

from cryptography.hazmat.primitives.serialization import load_pem_public_key

os.environ['JWKS_LIST'] = ''
from get_cookies import authenticator

#def test_get_public_key_success_single(monkeypatch, der, matching_jwks, valid_token):
#  #requests_mock.get('http://matching', text=matching_jwks)
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
