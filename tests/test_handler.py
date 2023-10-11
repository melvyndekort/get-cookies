import pytest
import json

from pathlib import Path


@pytest.fixture
def api_gw_event():
  event = Path('tests/event.json').read_text()
  return json.loads(event)

def test_success(monkeypatch, api_gw_event):
  from get_cookies import handler

  def get_cookies(token, origin):
    return 'test'
  monkeypatch.setattr(handler.converter, 'get_cookies', get_cookies)

  resp = handler.handle(api_gw_event, None)
  assert resp['statusCode'] == 200
  assert resp['body'] == '"test"'
  assert resp['headers']['Access-Control-Allow-Origin'] == 'http://localhost'

def test_fail(monkeypatch, api_gw_event):
  from get_cookies import handler

  def get_cookies(token, origin):
    raise Exception('My custom error')
  monkeypatch.setattr(handler.converter, 'get_cookies', get_cookies)

  resp = handler.handle(api_gw_event, None)
  assert resp['statusCode'] == 401
  assert resp['body'] == 'Unauthorized'
