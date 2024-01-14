terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "eu-central-1"
}

data "aws_partition" "current" {}

locals {
  lambda_function_name          = "BatteryHealthParser"
  lambda_runtime                = "python3.10"
  lambda_root                   = "${path.module}/python"
  lambda_layer_root             = "${local.lambda_root}/layer"
  lambda_layer_requirements_txt = "${local.lambda_layer_root}/requirements.txt"
  lambda_layer_lib_root = "${local.lambda_layer_root}/python"
  lambda_function_root  = "${local.lambda_root}/src"
}

resource "aws_iam_role" "lambda" {
  name_prefix = "Lambda-${local.lambda_function_name}-"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "sts:AssumeRole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })

  managed_policy_arns = [
    "arn:${data.aws_partition.current.partition}:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  ]
}

resource "null_resource" "pip_install" {
  provisioner "local-exec" {
    command = "pip install --quiet --requirement ${local.lambda_layer_requirements_txt} --target ${local.lambda_layer_lib_root}"
  }
}

data "archive_file" "lambda_layer" {
  depends_on  = [null_resource.pip_install]
  type        = "zip"
  source_dir  = local.lambda_layer_root
  output_path = "${path.module}/lambda_layer.zip"
}

resource "aws_lambda_layer_version" "layer" {
  layer_name          = "${local.lambda_function_name}-pip-requirements"
  filename            = data.archive_file.lambda_layer.output_path
  compatible_runtimes = [local.lambda_runtime]
}

data "archive_file" "lambda_function" {
  type        = "zip"
  source_dir  = local.lambda_function_root
  output_path = "${path.module}/lambda_function.zip"
}

resource "aws_lambda_function" "lambda" {
  filename         = data.archive_file.lambda_function.output_path
  function_name    = local.lambda_function_name
  role             = aws_iam_role.lambda.arn
  timeout          = 10
  handler          = "battery_status.lambda_handler"
  runtime          = local.lambda_runtime
  layers           = [aws_lambda_layer_version.layer.arn]
}