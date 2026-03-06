# Package the Lambda function
data "archive_file" "anomaly_detector" {
  type        = "zip"
  source_file = "../lambda/anomaly_detector/handler.py"
  output_path = "../lambda/anomaly_detector/handler.zip"
}

# Lambda function
resource "aws_lambda_function" "anomaly_detector" {
  filename         = data.archive_file.anomaly_detector.output_path
  function_name    = "anomaly-detector"
  role             = aws_iam_role.lambda_role.arn
  handler          = "handler.lambda_handler"
  runtime          = "python3.11"
  timeout          = 30
  source_code_hash = data.archive_file.anomaly_detector.output_base64sha256

  environment {
    variables = {
      SENSOR_TABLE  = aws_dynamodb_table.sensor_data.name
      ANOMALY_TABLE = aws_dynamodb_table.anomaly_alerts.name
    }
  }

  tags = {
    Project = "Edge-Cloud-Gateway"
    Env     = "dev"
  }
}

# Trigger Lambda every 5 minutes via EventBridge
resource "aws_cloudwatch_event_rule" "anomaly_schedule" {
  name                = "anomaly-detector-schedule"
  description         = "Run anomaly detector every 5 minutes"
  schedule_expression = "rate(5 minutes)"
}

resource "aws_cloudwatch_event_target" "anomaly_lambda" {
  rule      = aws_cloudwatch_event_rule.anomaly_schedule.name
  target_id = "AnomalyDetector"
  arn       = aws_lambda_function.anomaly_detector.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.anomaly_detector.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.anomaly_schedule.arn
}
