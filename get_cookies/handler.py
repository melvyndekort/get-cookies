import logging
import json
import os

from get_cookies import converter

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Secure CORS origin validation
ALLOWED_ORIGINS = set(origin.strip() for origin in os.environ.get('ALLOWED_ORIGINS', '').split(',') if origin.strip())

def _validate_origin(origin):
    """Validate origin against allowed origins list."""
    logger.info(f'CORS Debug - Origin received: "{origin}"')
    logger.info(f'CORS Debug - ALLOWED_ORIGINS env var: "{os.environ.get("ALLOWED_ORIGINS", "NOT_SET")}"')
    logger.info(f'CORS Debug - Parsed ALLOWED_ORIGINS set: {ALLOWED_ORIGINS}')
    
    if not origin or origin == '*':
        logger.warning(f'CORS Debug - Invalid origin format: {origin}')
        return False
    
    result = origin in ALLOWED_ORIGINS
    logger.info(f'CORS Debug - Validation result for "{origin}": {result}')
    return result

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
    logger.info(f'Handler Debug - Full event: {json.dumps(event)}')
    
    origin = event.get('headers', {}).get('origin')
    logger.info(f'Handler Debug - Extracted origin: "{origin}"')
    
    # Validate origin early for security
    if not _validate_origin(origin):
        logger.warning(f'Handler Debug - Origin validation failed for: {origin}')
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
