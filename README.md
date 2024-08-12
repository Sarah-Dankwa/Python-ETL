# de-alapin-totesys
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


