import os
import time
import pytest

@pytest.mark.parametrize("token_exp,expected_range", [
    (123, (6, 8)),  # Short expiration -> 7 days
    (32472144000000, None)  # Long expiration -> use token exp
])
def test_get_cookies_expiration_logic(monkeypatch, prep_authenticator, prep_signer, token_exp, expected_range):
    """Test expiration logic with different token expiration times."""
    from get_cookies import converter, authenticator

    def get_expiration(token):
        return token_exp
    monkeypatch.setattr(authenticator, 'get_expiration', get_expiration)

    os.environ['KEY_ID'] = "test"

    result = converter.get_cookies('token', 'origin')

    assert 'Policy' in result
    assert 'Signature' in result
    assert result['Key'] == 'test'
    
    if expected_range:
        # Short expiration case - should be extended to ~7 days
        current_time_ms = round(time.time() * 1000)
        days_min, days_max = expected_range
        assert result['Expiration'] > current_time_ms + (1000 * 60 * 60 * 24 * days_min)
        assert result['Expiration'] < current_time_ms + (1000 * 60 * 60 * 24 * days_max)
    else:
        # Long expiration case - should use token expiration
        assert result['Expiration'] == token_exp

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
