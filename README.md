## Intro.

This repository contains a simple example where Terraform deploys a Python function onto AWS Lambda.
The Python function accepts a Hexadecimal encoded message into respective fields and returns the result
in JSON format.


## How to run it?

Pre-requisites:

- Terraform
- AWS CLI

Export your AWS credentials as environment variables:
```
export AWS_ACCESS_KEY_ID="aws_access_key_id_value"
export AWS_SECRET_ACCESS_KEY="aws_secret_access_key_value"
```

From the project root folder run:

```
terraform init & terraform apply
```