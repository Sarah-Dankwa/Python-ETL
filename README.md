# de-alapin-totesys

# Totesys - ETL Pipeline

Final project in Northcoders Data Engineering Bootcamp: a data pipeline for a company selling tote bags. The brief is to create a data pipeline that will **extract** data from a pre-populated Totesys OLTP database. It archives this data in an AWS hosted data lake then **transforms** this data into a provided database schema, then **loads** it into a data warehouse hosted in AWS.

## Installation

Run make requirements to install all the python dependencies.

```bash
make requirements
```

Export AWS credentials to terminal to ensure terraform deploys to correct account and access to secret manager:
Credentials will be shared by AWS user with shared account

	export AWS_ACCESS_KEY_ID=<accesskey>
	export AWS_SECRET_ACCESS_KEY=<secret accesskey>
	export AWS_DEFAULT_REGION=eu-west-2

Then run terraform init

```bash
terraform init
```

## Execution and Usage



## Used Technologies

**Programming**
- Python
- Makefile

**Amazon Web Services**
- Alerts & Metrics
- Cloudwatch
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
- Pytest
- TDD
- Mocking & Patching

## Current Features
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
- [Alex Beveridge](https://github.com/bevs55)
- [Hanna Wang](https://github.com/Hana-Wang)
- [Jessica Marcell](https://github.com/Pringading)
- [Mohankumar Nanjegowda](https://github.com/Mohan0501)
- [Sarah Dankwa](https://github.com/Sarah-Dankwa)
- [Northcoders](https://github.com/northcoders)

## badges
![deploy workflow](https://github.com/Mohan0501/de-alapin-totesys/actions/workflows/deploy.yml/badge.svg)

![pandas](https://img.shields.io/badge/Amazon_AWS-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)

![pandas](https://img.shields.io/badge/Pandas-2C2D72?style=for-the-badge&logo=pandas&logoColor=white)

![python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)

![terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)

[![Trello](https://img.shields.io/badge/Trello-0052CC?style=for-the-badge&logo=trello&logoColor=white)](https://trello.com/b/mk8ELtrn/7dealapintoteskanban)



Project Repo

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


