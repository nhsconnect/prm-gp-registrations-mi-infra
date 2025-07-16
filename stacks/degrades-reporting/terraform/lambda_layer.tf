resource "aws_lambda_layer_version" "degrades" {
  layer_name               = "${var.environment}_degrades_lambda_layer"
  compatible_runtimes      = ["python3.12"]
  compatible_architectures = ["x86_64"]
  source_code_hash         = filebase64sha256("${var.degrades_lambda_layer_zip}")
  filename                 = var.degrades_lambda_layer_zip
}

resource "aws_lambda_layer_version" "pandas" {
  layer_name               = "${var.environment}_degrades_lambda_layer"
  compatible_runtimes      = ["python3.12"]
  compatible_architectures = ["x86_64"]
  source_code_hash         = filebase64sha256("${var.pandas_lambda_layer_zip}")
  filename                 = var.pandas_lambda_layer_zip
}

resource "aws_iam_policy" "lambda_layer" {
  name = "lambda_layer_policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "lambda:GetLayerVersion",
          "lambda:ListLayerVersions",
          "lambda:ListLayers"
        ],
        Resource = [
          "${aws_lambda_layer_version.degrades.arn}:*",
          "${aws_lambda_layer_version.pandas.arn}:*"
        ]
      }
    ]
  })
}