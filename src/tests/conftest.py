import os
import pytest
import requests
import json

@pytest.fixture
def prep_authenticator(requests_mock):
  os.environ['JWKS_LIST'] = 'http://localhost'
  requests_mock.get('http://localhost', text='{}')

@pytest.fixture
def prep_signer(requests_mock):
  os.environ['CLOUDFRONT_PK_PATH'] = 'test'
  param = {
    'Parameter': {
      'Value': """-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQCi8ViZH6DaJBpYcYDn/lGNmcuZLqmyC9xQzskknXPR9jfN15Zd
xhZehgyQjhNy4msk7g1f553zRr5wWVGkU4RcQIi5H6UGxD9JOVjaY4aa+9BTLt6E
hPMPdPEWP7ucFRFyaeuTzYPyYAac9cy8SHIIq4htf18pVCX+48IfsfBUsQIDAQAB
AoGBAIEPUpKuN5SwxeFJvcWDbYsPxvDEwgpRVKb4st76i5NBR0AWQ3ZxAKTL3kXd
EtCLQDxXBWbyKOxZG1wXkw/qSsoWYXpzfbFMOYvpA2znP93smFUMwGoOIDn37nU5
u6VlqLUZ7RRQYhFzSdjiySU5lJt+DpEAWBDP7/Fr+J1+C8exAkEA3pspeigZczHx
276sBjQ6O+Zd1uoVCFNr7hFy041N0bl5FdCf/v4hVLzer9QYypLrPKL1Qg78wSaQ
V5InCSLQXQJBALti6DDCOnk8hvVyqKheZAWkXSaSRBC9uMMSpXBPMdNI7bEHEkwV
BPaeKI7wzVas1z3qE1tgZMuwX/H7ikFCoGUCQQDX7MX02gSluqKRtogClJKQG8qW
dwTjyJd+m6o4Dm6XqkMLqAwqObN3EKUpBKDvjkdjz+X6p7MAYDnO19PJht15AkBY
3Mutq74dFkYOCeTPi4u1XT/LdduPcNk4sRQBkZzYTKJjrC3SJLmo1lH3j1xhOTAN
rX6me6zxJ2AomhfzYMw9AkBCsKc0UlfKkrqWWfUBJ2rWDuVlueaA9zLXamfQR4DM
ugdloV4hYHjlw0/iz3BZKEoF9Pcd+6H6EcaitIl0uL7f
-----END RSA PRIVATE KEY-----"""
    }
  }
  requests_mock.get(f'http://localhost:2773/systemsmanager/parameters/get?name={os.environ["CLOUDFRONT_PK_PATH"]}&withDecryption=true', text=json.dumps(param))