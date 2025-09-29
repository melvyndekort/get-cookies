import base64
import pytest

def test_sign(prep_signer):
    from get_cookies import signer

    expire_date = '123456'
    resource = 'test-resource'

    cookie = signer.generate_expiring_signed_cookie(resource, expire_date)
    
    # Test structure
    assert cookie['Expiration'] == expire_date
    assert cookie['Key'] == 'test'
    assert 'Policy' in cookie
    assert 'Signature' in cookie
    
    # Test that Policy and Signature are valid base64
    try:
        base64.b64decode(cookie['Policy'].replace('-', '+').replace('_', '=').replace('~', '/'))
        base64.b64decode(cookie['Signature'].replace('-', '+').replace('_', '=').replace('~', '/'))
    except Exception as e:
        pytest.fail(f"Invalid base64 encoding: {e}")
    
    # Test that policy contains expected resource
    policy_decoded = base64.b64decode(cookie['Policy'].replace('-', '+').replace('_', '=').replace('~', '/'))
    assert resource.encode() in policy_decoded
