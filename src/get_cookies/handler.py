import os
import logging
import json

from get_cookies import converter

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handle(event, context):
  try:
    token = event['queryStringParameters']['id_token']
    origin = event['headers']['origin']

    cookies = converter.get_cookies(token, origin)

    resp = {
      'statusCode': 200,
      'headers': {
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
      },
      'body': json.dumps(cookies)
    }
    return resp

  except Exception as e:
    logger.exception("Exception occurred")

    resp = {
      'statusCode': 401,
      'headers': {
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
      },
      'body': 'Unauthorized'
    }
    return resp
