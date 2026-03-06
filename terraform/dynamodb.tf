resource "aws_dynamodb_table" "sensor_data" {
  name         = "dht22-sensor-data"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "device_id"
  range_key    = "timestamp"

  attribute {
    name = "device_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  tags = {
    Project = "Edge-Cloud-Gateway"
    Env     = "dev"
  }
}
