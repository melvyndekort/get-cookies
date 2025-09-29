import logging
import json

from get_cookies import converter

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def _get_cors_headers(origin):
    return {
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
    }


def handle(event, context):
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

    except Exception as e:
        logger.exception(f'Exception occurred: {e}')

        return {
            'statusCode': 401,
            'headers': _get_cors_headers(origin),
            'body': 'Unauthorized'
        }
