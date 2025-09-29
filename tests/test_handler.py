import pytest
import json
import os
import sys
from pathlib import Path


@pytest.fixture
def api_gw_event():
    event = Path('tests/event.json').read_text()
    return json.loads(event)

def test_success(monkeypatch, api_gw_event):
    # Set allowed origins for test before importing
    monkeypatch.setenv('ALLOWED_ORIGINS', 'http://localhost')
    
    # Clear module cache to force reload with new env var
    if 'get_cookies.handler' in sys.modules:
        del sys.modules['get_cookies.handler']
    
    from get_cookies import handler

    def get_cookies(token, origin):
        return 'test'
    monkeypatch.setattr(handler.converter, 'get_cookies', get_cookies)

    resp = handler.handle(api_gw_event, None)
    assert resp['statusCode'] == 200
    assert resp['body'] == '"test"'
    assert resp['headers']['Access-Control-Allow-Origin'] == 'http://localhost'

def test_fail(monkeypatch, api_gw_event):
    # Set allowed origins for test before importing
    monkeypatch.setenv('ALLOWED_ORIGINS', 'http://localhost')
    
    # Clear module cache to force reload with new env var
    if 'get_cookies.handler' in sys.modules:
        del sys.modules['get_cookies.handler']
    
    from get_cookies import handler

    def get_cookies(token, origin):
        raise Exception('My custom error')
    monkeypatch.setattr(handler.converter, 'get_cookies', get_cookies)

    resp = handler.handle(api_gw_event, None)
    assert resp['statusCode'] == 401
    assert resp['body'] == 'Unauthorized'

def test_cors_headers_consistency(monkeypatch, api_gw_event):
    """Test that CORS headers are consistent between success and error responses."""
    # Set allowed origins for test before importing
    monkeypatch.setenv('ALLOWED_ORIGINS', 'http://localhost')
    
    # Clear module cache to force reload with new env var
    if 'get_cookies.handler' in sys.modules:
        del sys.modules['get_cookies.handler']
    
    from get_cookies import handler

    def get_cookies_success(token, origin):
        return {'test': 'data'}
    
    def get_cookies_error(token, origin):
        raise ValueError('Test error')
    
    # Test success response
    monkeypatch.setattr(handler.converter, 'get_cookies', get_cookies_success)
    success_resp = handler.handle(api_gw_event, None)
    
    # Test error response  
    monkeypatch.setattr(handler.converter, 'get_cookies', get_cookies_error)
    error_resp = handler.handle(api_gw_event, None)
    
    # CORS headers should be identical
    assert success_resp['headers']['Access-Control-Allow-Origin'] == error_resp['headers']['Access-Control-Allow-Origin']
    assert success_resp['headers']['Access-Control-Allow-Methods'] == error_resp['headers']['Access-Control-Allow-Methods']

def test_invalid_origin_blocked(monkeypatch):
    """Test that invalid origins are blocked for security."""
    # Set allowed origins for test (not including evil.com)
    monkeypatch.setenv('ALLOWED_ORIGINS', 'http://localhost')
    
    # Clear module cache to force reload with new env var
    if 'get_cookies.handler' in sys.modules:
        del sys.modules['get_cookies.handler']
    
    from get_cookies import handler
    
    # Test with malicious origin
    event = {
        'headers': {'origin': 'https://evil.com'},
        'queryStringParameters': {'id_token': 'test'}
    }
    
    resp = handler.handle(event, None)
    assert resp['statusCode'] == 403
    assert resp['body'] == 'Forbidden'
    assert resp['headers']['Access-Control-Allow-Origin'] == 'null'
