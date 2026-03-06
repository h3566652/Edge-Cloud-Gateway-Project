# IAM Role for IoT → DynamoDB
resource "aws_iam_role" "iot_dynamodb_role" {
  name = "iot-dynamodb-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = { Service = "iot.amazonaws.com" }
        Action    = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "iot_dynamodb_policy" {
  name = "iot-dynamodb-policy"
  role = aws_iam_role.iot_dynamodb_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = [
          "dynamodb:PutItem",
          "dynamodb:UpdateItem"
        ]
        Resource = aws_dynamodb_table.sensor_data.arn
      }
    ]
  })
}
