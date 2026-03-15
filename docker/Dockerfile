# Base image - lightweight Python on ARM64 (Raspberry Pi)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for DHT22 sensor
RUN apt-get update && apt-get install -y \
    libgpiod-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir \
    adafruit-circuitpython-dht \
    asyncua \
    awsiotsdk \
    lgpio

# Copy scripts
COPY scripts/ ./scripts/

# Default command (overridden per Pod in Kubernetes)
CMD ["python3", "scripts/opcua_server.py"]
