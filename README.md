# Smart Factory IoT Platform
### Raspberry Pi 5 × OPC UA × AWS IoT Core × Terraform

A production-style industrial IoT platform simulating smart factory 
edge-to-cloud architecture. Real sensor data flows through an OPC UA 
industrial protocol layer, through an edge gateway, to AWS cloud 
infrastructure with AI-powered anomaly detection.

---

## Architecture
```
DHT22 Sensor (GPIO4)
        ↓
OPC UA Server (Raspberry Pi 5)
— ISA-95 factory hierarchy —
Factory_Seoul → ProductionLine_A1 → Equipment_EnvMonitor_01 → Sensors
        ↓ opc.tcp://localhost:4840
OPC UA Client (Raspberry Pi 5)
— protocol translation: OPC UA → MQTT —
        ↓ MQTT/TLS port 8883 / X.509 auth
AWS IoT Core (ap-northeast-2)
        ↓ Rules Engine (DynamoDBv2)
DynamoDB — dht22-sensor-data
        ↓ EventBridge (every 5 min)
Lambda — Z-score anomaly detection
        ↓
DynamoDB — anomaly-alerts

All infrastructure provisioned with Terraform
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Hardware | Raspberry Pi 5, DHT22 sensor |
| Industrial Protocol | OPC UA (asyncua), ISA-95 hierarchy |
| Edge → Cloud | MQTT over TLS, port 8883 |
| Authentication | X.509 mutual TLS, AWS IoT Policies |
| Cloud Ingestion | AWS IoT Core, Rules Engine |
| Storage | AWS DynamoDB (on-demand) |
| AI/Analytics | AWS Lambda, Z-score anomaly detection |
| Scheduling | AWS EventBridge (5 min intervals) |
| Infrastructure | Terraform (IaC) |
| Language | Python 3 |

---

## Project Structure
```
Edge-Cloud-Gateway-Project/
├── scripts/
│   ├── sensor_to_aws.py        # Direct MQTT pipeline
│   ├── opcua_server.py         # OPC UA server (ISA-95 hierarchy)
│   ├── opcua_client.py         # OPC UA client → AWS IoT Core
│   └── test_sensor.py          # Sensor standalone test
├── lambda/
│   └── anomaly_detector/
│       └── handler.py          # Z-score anomaly detection
├── terraform/
│   ├── main.tf                 # Provider config
│   ├── iot.tf                  # IoT Core Thing, Policy, Rule
│   ├── dynamodb.tf             # Sensor data + anomaly tables
│   ├── iam.tf                  # IAM roles and policies
│   └── lambda.tf               # Lambda + EventBridge schedule
├── requirements.txt
├── iot-policy.json
├── .env.example
└── README.md
```

---

## Setup Instructions

### Prerequisites
- Raspberry Pi 5 with Raspberry Pi OS
- AWS account (free tier sufficient)
- Python 3.9+
- Terraform v1.0+
- AWS CLI configured

### 1. Clone the repository
```bash
git clone https://github.com/h3566652/Edge-Cloud-Gateway-Project.git
cd Edge-Cloud-Gateway-Project
```

### 2. Install dependencies on Raspberry Pi
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

### 4. Deploy AWS infrastructure
```bash
cd terraform
terraform init
terraform apply
```

### 5. Run OPC UA pipeline (two terminals)

Terminal 1 — Start OPC UA Server:
```bash
source venv/bin/activate
python3 scripts/opcua_server.py
```

Terminal 2 — Start OPC UA Client:
```bash
source venv/bin/activate
python3 scripts/opcua_client.py
```

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

## Key Features

**Industrial Protocol Layer (OPC UA)**
Models factory equipment following the ISA-95 manufacturing hierarchy standard. The OPC UA server exposes sensor data as structured industrial objects — the same pattern used in real smart factory deployments at Samsung, LG, and Siemens.

**Secure Edge-to-Cloud Communication**
All data transmission uses MQTT over TLS (port 8883) with X.509 mutual authentication. The device certificate uniquely identifies the Raspberry Pi to AWS, following the same security model used in production IoT deployments.

**AI-Powered Anomaly Detection**
AWS Lambda runs Z-score statistical analysis every 5 minutes, comparing the latest sensor reading against a 24-hour baseline. Readings beyond 2 standard deviations are flagged as anomalies and stored in a dedicated DynamoDB table — simulating predictive maintenance logic.

**Infrastructure as Code**
The entire AWS infrastructure is defined in Terraform, meaning the full cloud setup can be reproduced in any region with a single `terraform apply` command.

---

## Security Notes

- Certificates are gitignored and never committed
- IoT Policy follows least-privilege principle
- Dedicated IAM user (`terraform-admin`) for infrastructure management
- All MQTT traffic encrypted via TLS 1.2+

---

## Roadmap

- [ ] Kubernetes containerization (Docker + k3s)
- [ ] CI/CD pipeline (GitHub Actions + ArgoCD)
- [ ] Modbus TCP simulation for legacy PLC integration
- [ ] Real-time dashboard (Grafana / AWS QuickSight)
- [ ] OEE (Overall Equipment Effectiveness) calculator

---

## Author

KyoungMin Park | Cloud/IoT Project Developer
[LinkedIn](https://www.linkedin.com/in/kyoung-min-park-7801a3260/) | 
[GitHub](https://github.com/h3566652) |
[Tech Blog](https://kyoungminp00.tistory.com/)