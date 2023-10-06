import pytest

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
