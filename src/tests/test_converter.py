import pytest
import os

def test_get_cookies_success(monkeypatch, prep_authenticator, prep_signer):
  from get_cookies import converter, authenticator, signer

  def get_expiration(token):
    return 123
  monkeypatch.setattr(authenticator, 'get_expiration', get_expiration)

  os.environ['KEY_ID'] = "test"

  token = 'token'
  origin = 'origin'
  result = converter.get_cookies(token, origin)

  assert 'Policy' in result
  assert 'Signature' in result
  assert result['Expiration'] == 123
  assert result['Key'] == 'test'
