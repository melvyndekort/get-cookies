def test_sign(prep_signer):
  from get_cookies import signer

  expire_date = '123456'

  cookie = signer.generate_expiring_signed_cookie('resource', expire_date)
  assert cookie['Expiration'] == expire_date
  assert cookie['Key'] == 'test'
