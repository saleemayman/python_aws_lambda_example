## Intro.

This repository contains a simple example where Terraform deploys a Python function onto AWS Lambda.
The Python function accepts a Hexadecimal encoded message into respective fields and returns the result
in JSON format.


## How to run it?

Pre-requisites:

- Terraform
- AWS CLI


From the project root folder run:
```
terraform init & terraform apply
```