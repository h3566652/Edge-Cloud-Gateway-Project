import json
import boto3
from datetime import datetime, timedelta
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')
sensor_table = dynamodb.Table('dht22-sensor-data')
anomaly_table = dynamodb.Table('anomaly-alerts')

DEVICE_ID = 'rpi-dht22-seoul-001'

def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def lambda_handler(event, context):
    path   = event.get('rawPath', '')
    method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')

    if path == '/sensors/latest':
        return get_latest_sensor()
    elif path == '/sensors/history':
        return get_sensor_history()
    elif path == '/anomalies':
        return get_anomalies()
    else:
        return response(404, {'error': 'endpoint not found'})

def get_latest_sensor():
    result = sensor_table.query(
        KeyConditionExpression='device_id = :id',
        ExpressionAttributeValues={':id': DEVICE_ID},
        ScanIndexForward=False,
        Limit=1
    )
    items = result.get('Items', [])
    if not items:
        return response(404, {'error': 'no data found'})
    return response(200, items[0])

def get_sensor_history():
    start_time = int((datetime.now() - timedelta(hours=24)).timestamp())
    result = sensor_table.query(
        KeyConditionExpression='device_id = :id AND #ts >= :start',
        ExpressionAttributeNames={'#ts': 'timestamp'},
        ExpressionAttributeValues={
            ':id': DEVICE_ID,
            ':start': start_time
        }
    )
    return response(200, {
        'device_id': DEVICE_ID,
        'count': len(result['Items']),
        'readings': result['Items']
    })

def get_anomalies():
    result = anomaly_table.query(
        KeyConditionExpression='device_id = :id',
        ExpressionAttributeValues={':id': DEVICE_ID},
        ScanIndexForward=False,
        Limit=10
    )
    return response(200, {
        'device_id': DEVICE_ID,
        'anomalies': result['Items']
    })

def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body, default=decimal_to_float)
    }
