# IoT Thing
resource "aws_iot_thing" "dht22" {
  name = "rpi-dht22-seoul-001"
}

# IoT Policy
resource "aws_iot_policy" "dht22_policy" {
  name = "rpi-dht22-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "iot:Connect"
        Resource = "arn:aws:iot:ap-northeast-2:*:client/rpi-dht22-*"
      },
      {
        Effect   = "Allow"
        Action   = ["iot:Publish", "iot:Receive"]
        Resource = "arn:aws:iot:ap-northeast-2:*:topic/sensors/dht22/*"
      },
      {
        Effect   = "Allow"
        Action   = "iot:Subscribe"
        Resource = "arn:aws:iot:ap-northeast-2:*:topicfilter/sensors/dht22/*"
      }
    ]
  })
}

# IoT Rule → DynamoDB
resource "aws_iot_topic_rule" "dht22_to_dynamodb" {
  name        = "dht22_to_dynamodb"
  enabled     = true
  sql         = "SELECT device_id, timestamp, temperature, humidity FROM 'sensors/dht22/data'"
  sql_version = "2016-03-23"

  dynamodbv2 {
    role_arn = aws_iam_role.iot_dynamodb_role.arn

    put_item {
      table_name = aws_dynamodb_table.sensor_data.name
    }
  }
}
