import asyncio
import board
import adafruit_dht
from asyncua import Server
from datetime import datetime

# DHT22 setup
dhtDevice = adafruit_dht.DHT22(board.D4)

async def main():
    # Initialize OPC UA Server
    server = Server()
    await server.init()

    # Server endpoint
    server.set_endpoint("opc.tcp://0.0.0.0:4840/factory/sensors/")
    server.set_server_name("Smart Factory Sensor Gateway")

    # Register namespace
    uri = "http://smartfactory.edge.gateway"
    idx = await server.register_namespace(uri)

    # Build factory hierarchy (ISA-95 standard)
    # Factory → Production Line → Equipment → Sensors
    objects     = server.get_objects_node()
    factory     = await objects.add_object(idx, "Factory_Seoul")
    prod_line   = await factory.add_object(idx, "ProductionLine_A1")
    equipment   = await prod_line.add_object(idx, "Equipment_EnvMonitor_01")
    sensors     = await equipment.add_object(idx, "Sensors")

    # Sensor variables
    temp_var      = await sensors.add_variable(idx, "Temperature", 0.0)
    humid_var     = await sensors.add_variable(idx, "Humidity", 0.0)
    status_var    = await sensors.add_variable(idx, "Status", "INITIALIZING")
    timestamp_var = await sensors.add_variable(idx, "Timestamp", datetime.now().isoformat())

    # Make variables writable
    await temp_var.set_writable()
    await humid_var.set_writable()
    await status_var.set_writable()
    await timestamp_var.set_writable()

    # Equipment metadata
    await equipment.add_variable(idx, "EquipmentID", "ENV-01-A1-SEOUL")
    await equipment.add_variable(idx, "Location",    "Seoul_Lab_Floor1")
    await equipment.add_variable(idx, "Model",       "DHT22-RaspberryPi5")

    print("OPC UA Server started at opc.tcp://0.0.0.0:4840/factory/sensors/")
    print("Hierarchy: Factory_Seoul → ProductionLine_A1 → Equipment_EnvMonitor_01 → Sensors")

    async with server:
        while True:
            try:
                temperature = dhtDevice.temperature
                humidity    = dhtDevice.humidity

                if temperature is not None and humidity is not None:
                    # Determine equipment status
                    if 15 <= temperature <= 30 and humidity <= 80:
                        status = "RUNNING"
                    elif temperature > 30 or humidity > 80:
                        status = "WARNING"
                    else:
                        status = "ALARM"

                    # Update OPC UA variables
                    await temp_var.write_value(round(temperature, 2))
                    await humid_var.write_value(round(humidity, 2))
                    await status_var.write_value(status)
                    await timestamp_var.write_value(datetime.now().isoformat())

                    print(f"[OPC UA Server] Temp: {temperature}C  Humidity: {humidity}%  Status: {status}")

            except RuntimeError as e:
                print(f"Sensor error: {e}")
                await status_var.write_value("ERROR")

            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
