import time
import json
import board
import adafruit_dht
from awscrt import mqtt
from awsiot import mqtt_connection_builder

# === CONFIG ===
ENDPOINT = "a1x71u4jsfn1px-ats.iot.ap-northeast-2.amazonaws.com"
CLIENT_ID = "rpi-dht22-seoul-001"
TOPIC     = "sensors/dht22/data"

CERT_PATH = "/home/kpark30525/iot-project/certs/bc9980380dcfc2a34256b732e4b49804a857b1763acdaf96caad2aa2cb0f45d7-certificate.pem.crt"
KEY_PATH  = "/home/kpark30525/iot-project/certs/bc9980380dcfc2a34256b732e4b49804a857b1763acdaf96caad2aa2cb0f45d7-private.pem.key"
CA_PATH   = "/home/kpark30525/iot-project/certs/AmazonRootCA1.pem"

# === SENSOR SETUP ===
dhtDevice = adafruit_dht.DHT22(board.D4)

# === AWS CONNECTION ===
def on_connection_success(connection, callback_data):
    print("Connected to AWS IoT Core!")

def on_connection_failure(connection, callback_data):
    print(f"Connection failed: {callback_data.error}")

mqtt_connection = mqtt_connection_builder.mtls_from_path(
    endpoint=ENDPOINT,
    cert_filepath=CERT_PATH,
    pri_key_filepath=KEY_PATH,
    ca_filepath=CA_PATH,
    client_id=CLIENT_ID,
    clean_session=False,
    keep_alive_secs=30,
    on_connection_success=on_connection_success,
    on_connection_failure=on_connection_failure
)

print("Connecting to AWS IoT Core...")
connect_future = mqtt_connection.connect()
connect_future.result()

# === MAIN LOOP ===
try:
    while True:
        try:
            temperature = dhtDevice.temperature
            humidity    = dhtDevice.humidity

            message = {
                "device_id":   CLIENT_ID,
                "timestamp":   int(time.time()),
                "temperature": round(temperature, 2),
                "humidity":    round(humidity, 2)
            }

            mqtt_connection.publish(
                topic=TOPIC,
                payload=json.dumps(message),
                qos=mqtt.QoS.AT_LEAST_ONCE
            )

            print(f"Published: {message}")

        except RuntimeError as e:
            print(f"Sensor error: {e}")

        time.sleep(60)

except KeyboardInterrupt:
    print("Stopping...")

finally:
    mqtt_connection.disconnect()
    dhtDevice.exit()
    print("Disconnected.")
