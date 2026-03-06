import board
import adafruit_dht
import time

dhtDevice = adafruit_dht.DHT22(board.D4)

while True:
    try:
        temperature = dhtDevice.temperature
        humidity = dhtDevice.humidity
        print(f"Temperature: {temperature:.1f}C  Humidity: {humidity:.1f}%")
    except RuntimeError as e:
        print(f"Sensor error: {e}")
    time.sleep(2)
