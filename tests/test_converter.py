import os
import time

def test_get_cookies_short_exp(monkeypatch, prep_authenticator, prep_signer):
    from get_cookies import converter, authenticator

    def get_expiration(token):
        return 123
    monkeypatch.setattr(authenticator, 'get_expiration', get_expiration)

    os.environ['KEY_ID'] = "test"

    token = 'token'
    origin = 'origin'
    result = converter.get_cookies(token, origin)

    assert 'Policy' in result
    assert 'Signature' in result
    assert result['Expiration'] > round(time.time() * 1000) + (1000 * 60 * 60 * 24 * 6)
    assert result['Expiration'] < round(time.time() * 1000) + (1000 * 60 * 60 * 24 * 8)
    assert result['Key'] == 'test'

def test_get_cookies_long_exp(monkeypatch, prep_authenticator, prep_signer):
    from get_cookies import converter, authenticator

    def get_expiration(token):
        return 32472144000000
    monkeypatch.setattr(authenticator, 'get_expiration', get_expiration)

    os.environ['KEY_ID'] = "test"

    token = 'token'
    origin = 'origin'
    result = converter.get_cookies(token, origin)

    assert 'Policy' in result
    assert 'Signature' in result
    assert result['Expiration'] == 32472144000000
    assert result['Key'] == 'test'
