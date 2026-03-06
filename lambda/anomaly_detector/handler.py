import json
import boto3
import math
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')
sensor_table = dynamodb.Table('dht22-sensor-data')
anomaly_table = dynamodb.Table('anomaly-alerts')

DEVICE_ID = 'rpi-dht22-seoul-001'
Z_SCORE_THRESHOLD = 2.0
LOOKBACK_HOURS = 24

def lambda_handler(event, context):
    # Get last 24 hours of readings
    start_time = int((datetime.now() - timedelta(hours=LOOKBACK_HOURS)).timestamp())

    response = sensor_table.query(
        KeyConditionExpression='device_id = :id AND #ts >= :start',
        ExpressionAttributeNames={'#ts': 'timestamp'},
        ExpressionAttributeValues={
            ':id': DEVICE_ID,
            ':start': start_time
        }
    )

    items = response['Items']

    if len(items) < 5:
        return {'statusCode': 400, 'body': 'Not enough data yet'}

    # Extract values
    temperatures = [float(item['temperature']) for item in items]
    humidities   = [float(item['humidity']) for item in items]

    # Calculate mean and standard deviation
    def mean(values):
        return sum(values) / len(values)

    def std(values):
        m = mean(values)
        variance = sum((x - m) ** 2 for x in values) / len(values)
        return math.sqrt(variance)

    temp_mean = mean(temperatures)
    temp_std  = std(temperatures)
    hum_mean  = mean(humidities)
    hum_std   = std(humidities)

    # Latest reading
    latest      = items[-1]
    latest_temp = float(latest['temperature'])
    latest_hum  = float(latest['humidity'])

    # Z-score calculation
    temp_z = abs((latest_temp - temp_mean) / temp_std) if temp_std > 0 else 0
    hum_z  = abs((latest_hum - hum_mean) / hum_std) if hum_std > 0 else 0

    # Anomaly detection
    anomalies = []

    if temp_z > Z_SCORE_THRESHOLD:
        anomalies.append({
            'type': 'TEMPERATURE_ANOMALY',
            'value': latest_temp,
            'mean': round(temp_mean, 2),
            'z_score': round(temp_z, 2),
            'message': f'Temperature {latest_temp}C is {round(temp_z, 1)} std deviations from mean ({round(temp_mean, 2)}C)'
        })

    if hum_z > Z_SCORE_THRESHOLD:
        anomalies.append({
            'type': 'HUMIDITY_ANOMALY',
            'value': latest_hum,
            'mean': round(hum_mean, 2),
            'z_score': round(hum_z, 2),
            'message': f'Humidity {latest_hum}% is {round(hum_z, 1)} std deviations from mean ({round(hum_mean, 2)}%)'
        })

    severity = 'NORMAL'
    if anomalies:
        severity = 'HIGH' if max(temp_z, hum_z) > 3 else 'MEDIUM'

    result = {
        'device_id':          DEVICE_ID,
        'timestamp':          int(datetime.now().timestamp()),
        'latest_temperature': latest_temp,
        'latest_humidity':    latest_hum,
        'temp_mean_24h':      round(temp_mean, 2),
        'hum_mean_24h':       round(hum_mean, 2),
        'temp_z_score':       round(temp_z, 2),
        'hum_z_score':        round(hum_z, 2),
        'anomalies':          anomalies,
        'severity':           severity,
        'total_readings':     len(items)
    }

    # Always store the result
    anomaly_table.put_item(Item={
        'device_id': DEVICE_ID,
        'timestamp': result['timestamp'],
        'severity':  severity,
        'details':   json.dumps(result)
    })

    print(f"Result: {json.dumps(result, indent=2)}")

    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
