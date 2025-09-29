import logging
import json

from get_cookies import converter

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def _get_cors_headers(origin):
    """Generate CORS headers for API Gateway response."""
    return {
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Origin': origin,
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
    origin = event.get('headers', {}).get('origin', '*')
    
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
