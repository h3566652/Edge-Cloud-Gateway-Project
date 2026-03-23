import asyncio
import json
import time
from asyncua import Client
from awscrt import mqtt
from awsiot import mqtt_connection_builder

import os

# AWS IoT Config

ENDPOINT = os.environ.get("AWS_IOT_ENDPOINT")
CLIENT_ID = os.environ.get("CLIENT_ID", "rpi-dht22-seoul-001")
TOPIC = os.environ.get("TOPIC", "sensors/dht22/data")
CERT_PATH = os.environ.get("CERT_PATH")
KEY_PATH = os.environ.get("KEY_PATH")
CA_PATH = os.environ.get("CA_PATH")

# OPC UA Server address

OPC_UA_URL = os.environ.get("OPC_UA_URL", "opc.tcp://opcua-server-service:4840/factory/sensors/")

async def main():
    await asyncio.sleep(10) # Wait for OPC UA server to be ready
    # Connect to AWS IoT Core
    print("Connecting to AWS IoT Core...")
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=ENDPOINT,
        cert_filepath=CERT_PATH,
        pri_key_filepath=KEY_PATH,
        ca_filepath=CA_PATH,
        client_id=CLIENT_ID,
        clean_session=False,
        keep_alive_secs=30
    )
    connect_future = mqtt_connection.connect()
    connect_future.result()
    print("Connected to AWS IoT Core!")

    # Connect to OPC UA Server
    async with Client(url=OPC_UA_URL) as client:
        print(f"Connected to OPC UA Server: {OPC_UA_URL}")

        # Navigate factory hierarchy to get sensor nodes
        root      = client.get_root_node()
        factory   = await root.get_child(["0:Objects", "2:Factory_Seoul"])
        prod_line = await factory.get_child(["2:ProductionLine_A1"])
        equipment = await prod_line.get_child(["2:Equipment_EnvMonitor_01"])
        sensors   = await equipment.get_child(["2:Sensors"])

        # Get variable nodes
        temp_node      = await sensors.get_child(["2:Temperature"])
        humid_node     = await sensors.get_child(["2:Humidity"])
        status_node    = await sensors.get_child(["2:Status"])
        equip_id_node  = await equipment.get_child(["2:EquipmentID"])
        location_node  = await equipment.get_child(["2:Location"])

        print("Navigated factory hierarchy successfully!")

        while True:
            try:
                # Read from OPC UA Server
                temperature  = await temp_node.read_value()
                humidity     = await humid_node.read_value()
                status       = await status_node.read_value()
                equipment_id = await equip_id_node.read_value()
                location     = await location_node.read_value()

                # Build industrial-style payload
                message = {
                    "device_id":    CLIENT_ID,
                    "equipment_id": equipment_id,
                    "location":     location,
                    "timestamp":    int(time.time()),
                    "temperature":  temperature,
                    "humidity":     humidity,
                    "status":       status,
                    "protocol":     "OPC-UA",
                    "source":       OPC_UA_URL
                }

                # Publish to AWS IoT Core
                mqtt_connection.publish(
                    topic=TOPIC,
                    payload=json.dumps(message),
                    qos=mqtt.QoS.AT_LEAST_ONCE
                )

                print(f"[OPC UA Client] Published: {equipment_id} | Temp: {temperature}C | Status: {status}")

            except Exception as e:
                print(f"Error: {e}")

            await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())
