import os
import pytest
import boto3

from pathlib import Path

from moto import mock_ssm

@pytest.fixture
def prep_authenticator(requests_mock):
  os.environ['JWKS_LIST'] = 'http://localhost'
  requests_mock.get('http://localhost', text='{}')

@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-1"
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"

@pytest.fixture
def prep_signer(aws_credentials):
  param_name = 'test'
  private_key = Path('tests/private.pem').read_text()
  
  os.environ['CLOUDFRONT_PK_PATH'] = param_name

  with mock_ssm():
    ssm = boto3.client("ssm")
    ssm.put_parameter(
      Name=param_name,
      Value=private_key,
      Type="SecureString",
    )
    yield
