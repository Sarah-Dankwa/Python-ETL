# Totesys - ETL Pipeline

Final project in Northcoders Data Engineering Bootcamp: a data pipeline for a company selling tote bags. The brief is to create a data pipeline that will **extract** data from a pre-populated Totesys OLTP database. It archives this data in an AWS-hosted data lake then **transforms** this data into a provided database schema, and then **loads** it into a data warehouse hosted in AWS.

![data pipeline](./mvp.png)

## Installation

Run make requirements to install all the python dependencies.

```bash
make requirements
```

**GitHub Secrets**

Add following secrets to github secrets

|Secret|Value|
|------|-----|
AWS_ACCESS_KEY_ID|aws secret access key
AWS_SECRET_ACCESS_KEY|aws secret access key
AWS_REGION|aws default region

**Resources to add in the AWS console**

Create secrets in secrets manager with the database credentials for the warehouse and the OLTP database:

**secret name: totesys-database**

Credentials for totesys OLTP database

|Key|Value|
|---|---|
|Database|name of totesys database
|Hostname|hostname of totesys database
|Username|username of totesys database
|Password|password of totesys database
|Port|5432


**secret name: totesys-warehouse**

Credentials for totesys data warehouse

|Key|Value|
|---|---|
|POSTGRES_DATABASE|name of data warehouse
|POSTGRES_HOSTNAME|hostname of data warehouse
|POSTGRES_USERNAME|username of data warehouse
|POSTGRES_PASSWORD|password of data warehouse
|POSTGRES_PORT| 5432


Update following resources to use the arns of these secrets:

terraform/iam_extract.tf - inside the following data block update the resources field to use arn of the *totesys-database* secret
```hcl
data "aws_iam_policy_document" "secret_manager_extract_document"{
    statement  {
      actions = [
        "secretsmanager:GetSecretValue"
      ]
      resources = ["arn:aws:secretsmanager:eu-west-2:590183674561:secret:totesys-database-1iOpWx",]
      effect = "Allow"
      sid = "AllowSecrets"
    }
}
```

terraform/iam_load.tf - inside the following data block update the resources field to use arn of the *totesys-warehouse* secret
```hcl
data "aws_iam_policy_document" "secret_manager_document_warehouse"{
    statement  {
      actions = [
        "secretsmanager:GetSecretValue"
      ]
      resources = ["arn:aws:secretsmanager:eu-west-2:590183674561:secret:totesys-warehouse-ltGoRO",]
      effect = "Allow"
      sid = "AllowSecrets"
    }
}
```


Add S3 bucket for terraform state

Then update terraform/main.tf to use this bucket to store the tf state file
```hcl
backend "s3" {
    bucket = "nc-alapin-project-tf-state"
    key = "nc-alapin-project-tf-state/terraform.tfstate"
    region = "eu-west-2"
  }
```

**Deploying to AWS**

Export AWS credentials to terminal to ensure terraform deploys to correct account and access to secret manager:
Credentials will be shared by AWS user with shared account

	export AWS_ACCESS_KEY_ID=<accesskey>
	export AWS_SECRET_ACCESS_KEY=<secret accesskey>
	export AWS_DEFAULT_REGION=eu-west-2

Then run terraform init

```bash
terraform init
```

**Using the test database**

In order to run tests for the extract & load lambdas you will need to create a test postgresql database

Add following variables to a .env file
```text
LOCAL_USER=<your psql username>
LOCAL_PASSWORD=<your psql password>
LOCAL_DATABASE=test_warehouse
LOCAL_HOST=localhost
LOCAL_PORT=5432
DATA_INGESTED_BUCKET_NAME=test-ingestion-bucket
DATA_PROCESSED_BUCKET_NAME=test-processed-bucket
SNS_TOPIC_ARN=test-arn
```

then run the following command
```bash
make setup-db
```


## Execution and Usage

Tables ingeseted from original OLTP Database
|tablename|
|----------|
|counterparty|
|currency|
|department|
|design|
|staff|
|sales_order|
|address|
|payment|
|purchase_order|
|payment_type|
|transaction|


Schema of the final Data Warehouse ([Entity Relationship Diagram](https://dbdiagram.io/d/637a423fc9abfc611173f637))
|tablename|
|---------|
|fact_sales_order|
|dim_staff|
|dim_location|
|dim_design|
|dim_date|
|dim_currency|
|dim_counterparty|



## Used Technologies

**Programming Languages**
- Python
- Makefile
- HCL
- SQL

**Amazon Web Services**
- Alerts & Metrics
- Cloudwatch
- Eventbridge
- IAMs
- Lambda
- S3 Buckets
- Secrets Manager
- SSM Parameter Store
- Step functions

**Data Modelling**
- PostgreSQL
- pg8000 python library
- pandas libraray

**DevOps**
- Terraform
- Makefile
- GitHub Actions
- GitHub Secrets

**Testing**
- pytest library
- moto library
- unittest mock & patch

## Current Features

- Eventbridge - runs the step function every 15 minutes
- Step Function - runs the three lambdas in order.
- Extract lambda function - connects to external RDS using credentials uploaded to AWS secret manager. Saves data as parquet files in S3 bucket
- Lambda layer - all functions use custom pg8000 lambda layer and aws provided pandas layer.
- Ingested data S3 Bucket - stores all data by date & time uploaded
- Cloudwatch logs - gives info about which files have been changed and logs any errors that have occurred
- Alerts - Metric alarm monitors any alerts and sends emails using an SNS topic
- Transform lambda function - takes data from the S3 bucket, remodels data into the star schema of the final data warehouse, and saves the data in parquet files in the processed data bucket.
- Processed data S3 Bucket - Stores transformed data by date and time.
- Load lambda function - takes data from processed data bucket, uses database credentials uploaded to AWS Secrets Manager.
- *(Outside of this repo, a S3 bucket has been added to AWS to store the tf state file, and database credentials for the OLTP database & the data warehouse have been added to secrets manager in AWS)*


## Contributing

Export AWS credentials to terminal to ensure terraform deploys to correct account and access to secret manager:
Credentials will be shared by AWS user with shared account

	export AWS_ACCESS_KEY_ID=<accesskey>
	export AWS_SECRET_ACCESS_KEY=<secret accesskey>
	export AWS_DEFAULT_REGION=eu-west-2


Makefile
- make requirements (only once or when pip list updated)
- make dev setup
- make run-checks

Ensure venv is active and python path exported
- source venv/bin/activate
- export PYTHONPATH=$(pwd)


END OF DAY: Terraform destroy!

## Contributors

**TEAM de-Alapin-totesys**
- [Alex Beveridge](https://github.com/bevs55)
- [Hanna Wang](https://github.com/Hana-Wang)
- [Jessica Marcell](https://github.com/Pringading)
- [Mohankumar Nanjegowda](https://github.com/Mohan0501)
- [Sarah Dankwa](https://github.com/Sarah-Dankwa)
- [Northcoders](https://github.com/northcoders)


## Further Setup information

###########PROJECT##############

	useful design documentation can be found in documents folder

	Kanban Board:
	https://trello.com/b/mk8ELtrn/7dealapintoteskanban


##########PROJECT STRUCTURE##########

GitHub/workflow/
- deploy.yml

src/
- lambda1.py
- lambda2……
test/
- testfile1.py
- testfile2.py
- ……etc
terraform/
- IAM
- s3
- main
- stepfunction
- logger
- ….. etc

.gitignore

README.md

MAKEFILE

DOCUMENTS/
- useful files for design / understanding


#############DAILY SETUP################

Export AWS credentials to terminal to ensure terraform deploys to correct account and access to secret manager:
Credentials will be shared by AWS user with shared account

	export AWS_ACCESS_KEY_ID=<accesskey>
	export AWS_SECRET_ACCESS_KEY=<secret accesskey>
	export AWS_DEFAULT_REGION=eu-west-2


Makefile
- make requirements (only once or when pip list updated)
- make dev setup
- make run-checks

Ensure venv is active and python path exported
- source venv/bin/activate
- export PYTHONPATH=$(pwd)


END OF DAY: Terraform destroy!


#############TESTING##################

Use of purest is required

Where applicable AWS Moto mocking should be applied



###########CICD####################### 

checks will be performed upon pull requests and push to main.

## Badges
![deploy workflow](https://github.com/Mohan0501/de-alapin-totesys/actions/workflows/deploy.yml/badge.svg)

![Amazon AWS](https://img.shields.io/badge/Amazon_AWS-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)

![GitHub Actions](https://img.shields.io/badge/Github%20Actions-282a2e?style=for-the-badge&logo=githubactions&logoColor=367cfe)

![pandas](https://img.shields.io/badge/Pandas-2C2D72?style=for-the-badge&logo=pandas&logoColor=white)

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)

![python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)

![slack](https://img.shields.io/badge/Slack-4A154B?style=for-the-badge&logo=slack&logoColor=white)

![terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)

[![Trello](https://img.shields.io/badge/Trello-0052CC?style=for-the-badge&logo=trello&logoColor=white)](https://trello.com/b/mk8ELtrn/7dealapintoteskanban)

![vscode](https://img.shields.io/badge/VSCode-0078D4?style=for-the-badge&logo=visual%20studio%20code&logoColor=white)
