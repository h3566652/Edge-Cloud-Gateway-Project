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
# API Handler Lambda
data "archive_file" "api_handler" {
  type        = "zip"
  source_file = "../lambda/api_handler/handler.py"
  output_path = "../lambda/api_handler/handler.zip"
}

resource "aws_lambda_function" "api_handler" {
  filename         = data.archive_file.api_handler.output_path
  function_name    = "iot-api-handler"
  role             = aws_iam_role.lambda_role.arn
  handler          = "handler.lambda_handler"
  runtime          = "python3.11"
  timeout          = 30
  source_code_hash = data.archive_file.api_handler.output_base64sha256

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

# API Gateway
resource "aws_apigatewayv2_api" "iot_api" {
  name          = "iot-sensor-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET"]
    allow_headers = ["*"]
  }

  tags = {
    Project = "Edge-Cloud-Gateway"
    Env     = "dev"
  }
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id                 = aws_apigatewayv2_api.iot_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.api_handler.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "sensors_latest" {
  api_id    = aws_apigatewayv2_api.iot_api.id
  route_key = "GET /sensors/latest"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_route" "sensors_history" {
  api_id    = aws_apigatewayv2_api.iot_api.id
  route_key = "GET /sensors/history"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_route" "anomalies" {
  api_id    = aws_apigatewayv2_api.iot_api.id
  route_key = "GET /anomalies"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.iot_api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.iot_api.execution_arn}/*/*"
}

output "api_endpoint" {
  value = aws_apigatewayv2_api.iot_api.api_endpoint
}
