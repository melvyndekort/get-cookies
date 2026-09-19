"""Lambda handler: converts a validated JWT into CloudFront signed cookies."""

import json
import logging
import os

from get_cookies import converter

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Secure CORS origin validation
ALLOWED_ORIGINS = set(
    origin.strip() for origin in os.environ.get('ALLOWED_ORIGINS', '').split(',') if origin.strip()
)

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


def handle(event, _context):
    """
    AWS Lambda handler for converting JWT tokens to CloudFront signed cookies.

    Args:
        event: API Gateway event containing query parameters and headers
        _context: Lambda context object (unused)

    Returns:
        dict: API Gateway response with signed cookies or error
    """
    origin = event.get('headers', {}).get('origin')

    # Validate origin early for security
    if not _validate_origin(origin):
        logger.warning('Invalid or missing origin: %s', origin)
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
        logger.error('Client error: %s', e)
        return {
            'statusCode': 400,
            'headers': _get_cors_headers(origin),
            'body': 'Bad Request'
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        # Top-level safety net: any unexpected error becomes a 401 rather
        # than leaking a 500 with a stack trace to the client.
        logger.exception('Server error: %s', e)
        return {
            'statusCode': 401,
            'headers': _get_cors_headers(origin),
            'body': 'Unauthorized'
        }
