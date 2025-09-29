import logging
import json
import os

from get_cookies import converter

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Secure CORS origin validation
ALLOWED_ORIGINS = set(os.environ.get('ALLOWED_ORIGINS', '').split(','))

def _validate_origin(origin):
    """Validate origin against allowed origins list."""
    if not origin or origin == '*':
        return False
    return origin in ALLOWED_ORIGINS

def _get_cors_headers(origin):
    """Generate CORS headers for API Gateway response."""
    validated_origin = origin if _validate_origin(origin) else None
    return {
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Origin': validated_origin or 'null',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
    }


def handle(event, context):
    """
    AWS Lambda handler for converting JWT tokens to CloudFront signed cookies.
    
    Args:
        event: API Gateway event containing query parameters and headers
        context: Lambda context object
        
    Returns:
        dict: API Gateway response with signed cookies or error
    """
    origin = event.get('headers', {}).get('origin')
    
    # Validate origin early for security
    if not _validate_origin(origin):
        logger.warning(f'Invalid or missing origin: {origin}')
        return {
            'statusCode': 403,
            'headers': _get_cors_headers(None),
            'body': 'Forbidden'
        }
    
    try:
        params = event.get('queryStringParameters') or {}
        token = params.get('id_token')
        
        if not token:
            raise ValueError("Missing id_token parameter")

        cookies = converter.get_cookies(token, origin)

        return {
            'statusCode': 200,
            'headers': _get_cors_headers(origin),
            'body': json.dumps(cookies)
        }

    except (KeyError, ValueError, TypeError) as e:
        logger.error(f'Client error: {e}')
        return {
            'statusCode': 400,
            'headers': _get_cors_headers(origin),
            'body': 'Bad Request'
        }
    except Exception as e:
        logger.exception(f'Server error: {e}')
        return {
            'statusCode': 401,
            'headers': _get_cors_headers(origin),
            'body': 'Unauthorized'
        }
