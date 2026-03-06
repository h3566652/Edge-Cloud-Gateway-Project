# Raspberry Pi DHT22 → AWS IoT Core Pipeline

A real-time IoT data pipeline that collects temperature and humidity data
from a DHT22 sensor connected to a Raspberry Pi 5, and streams it to AWS
IoT Core via MQTT over TLS for cloud storage and analysis.

---

## Problem Statement

Building automation and environmental monitoring systems often rely on
expensive proprietary hardware. This project demonstrates a low-cost,
scalable alternative using off-the-shelf components and AWS cloud
infrastructure — bridging the gap between embedded hardware and
cloud-native IoT platforms.

---

## Architecture
```
DHT22 Sensor (GPIO4)
        ↓
Raspberry Pi 5 — Python script
        ↓ MQTT over TLS / port 8883 / X.509 auth
AWS IoT Core (Thing: rpi-dht22-seoul-001)
        ↓ Rules Engine (DynamoDBv2)
DynamoDB (dht22-sensor-data)
├── device_id
├── timestamp
├── temperature
└── humidity
```

---

## Tech Stack

- **Hardware:** Raspberry Pi 5, DHT22 sensor, 10kΩ pull-up resistor
- **Language:** Python 3
- **Libraries:** `adafruit-circuitpython-dht`, `awsiotsdk`
- **Cloud:** AWS IoT Core (ap-northeast-2 / Seoul region)
- **Protocol:** MQTT over TLS (port 8883), X.509 certificates
- **Storage:** AWS DynamoDB (DynamoDBv2 via Rules Engine)

---

## Hardware Wiring
```
Raspberry Pi 5        DHT22 (bare sensor)
──────────────        ───────────────────
3.3V ─────────────── Pin 1 (VCC)
3.3V ──[10kΩ]─────── Pin 2 (DATA)
GPIO4 ────────────── Pin 2 (DATA)
                      Pin 3 (NC)
GND ──────────────── Pin 4 (GND)
```

---

## Setup Instructions

### Prerequisites
- Raspberry Pi 5 with Raspberry Pi OS
- AWS account (free tier sufficient)
- Python 3.9+

### 1. Clone the repository
```bash
git clone https://github.com/h3566652/Edge-Cloud-Gateway-Project.git
cd Edge-Cloud-Gateway-Project
```

### 2. Install dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. AWS IoT Core setup
- Create an IoT Thing named `rpi-dht22-seoul-001`
- Generate and download X.509 certificates
- Attach `iot-policy.json` to your certificate
- Place certificates in `certs/` directory

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env with your AWS endpoint and certificate paths
```

### 5. Run
```bash
python3 scripts/sensor_to_aws.py
```

---

## Project Structure
```
Edge-Cloud-Gateway-Project/
├── scripts/
│   ├── sensor_to_aws.py       # Main pipeline script
│   └── test_sensor.py         # Sensor standalone test
├── certs/                     # (gitignored) AWS certificates
├── docs/                      # Architecture diagrams, images
├── requirements.txt
├── iot-policy.json
├── .env.example
├── .gitignore
└── README.md
```

---

## Security Notes

- Certificates are gitignored and never committed to the repository
- IoT Policy follows least-privilege principle
- All MQTT traffic encrypted via TLS 1.2+

---

## Roadmap

- [ ] AI/anomaly detection on sensor data (AWS Lambda)
- [ ] Edge AI — lightweight model on Raspberry Pi
- [ ] Real-time dashboard (Grafana / AWS QuickSight)
- [ ] LLM-powered natural language query interface

---

## Author

Kyoung Min Park
[LinkedIn](https://www.linkedin.com/in/kyoung-min-park-7801a3260/) | [GitHub](https://github.com/h3566652)
