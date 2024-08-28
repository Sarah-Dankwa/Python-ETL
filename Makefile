#################################################################################
#
# Makefile to build the project
#
#################################################################################

PROJECT_NAME = DE-ALAPIN-TOTESYS
REGION = eu-west-2
PYTHON_INTERPRETER = python3
WD=$(shell pwd)
PYTHONPATH=${WD}
SHELL := /bin/bash
PROFILE = default
PIP:=pip3

## Create python interpreter environment.
create-environment:
	@echo ">>> About to create environment: $(PROJECT_NAME)..."
	@echo ">>> check python3 version"
	( \
		$(PYTHON_INTERPRETER) --version; \
	)
	@echo ">>> Setting up VirtualEnv."
	( \
	    $(PIP) install -q virtualenv virtualenvwrapper; \
	    virtualenv venv --python=$(PYTHON_INTERPRETER); \
	)

# Define utility variable to help calling Python from the virtual environment
# ACTIVATE_ENV := source venv/bin/activate

# Execute python related functionalities from within the project's environment
define execute_in_env
	(source venv/bin/activate && $1)
endef

## Set up log directory
logdirs:
	mkdir -p logs

## Build the environment requirements
requirements: create-environment logdirs
	$(call execute_in_env, $(PIP) install -r ./requirements.txt)

## Set up dependencies/python directory and install specific packages
custom-dependencies: create-environment logdirs
	
	@echo ">>> Setting up dependencies/python directory..."
	mkdir -p dependencies/python
##  rm -rf dependencies/python/*

##	@echo ">>> Installing pandas to dependencies/python..."
##	$(call execute_in_env, $(PIP) install pandas -t dependencies/python --no-cache-dir)

##  @echo ">>> Installing requirements.txt to dependencies/python..."
##  $(call execute_in_env, $(PIP) install -r ./requirements.txt -t dependencies/python --no-cache-dir)

	@echo ">>> Installing pg8000 to dependencies/python..."
	$(call execute_in_env, $(PIP) install pg8000 -t dependencies/python --no-cache-dir)
	@echo ">>> Installing forex_python to dependencies/python..."
	$(call execute_in_env, $(PIP) install forex_python -t dependencies/python --no-cache-dir)

	@echo ">>> Installing forex-python to dependencies/python..."
	$(call execute_in_env, $(PIP) install forex-python -t dependencies/python --no-cache-dir)

all-requirements: requirements custom-dependencies

## Run Terraform Init
terraform-init:
	@echo ">>> Initializing Terraform"
	cd terraform && terraform init

## Run Terraform Plan
terraform-plan: custom-dependencies terraform-init
	@echo ">>> Running Terraform Plan ..."
	cd terraform && terraform plan

## Run Terraform Apply
terraform-apply: custom-dependencies terraform-init
	@echo ">>> Running Terraform Apply ..."
	cd terraform && terraform apply -auto-approve

## Run Terraform Destroy
terraform-destroy: custom-dependencies terraform-init
	@echo ">>> Destroying Terraform-managed infrastructure ..."
	cd terraform && terraform destroy -auto-approve

# Clean up dependencies after deployment 
clean-dependencies:
	@echo ">>> Cleanig dependencies/python ..."
	rm -rf dependencies/python
## rm -rf venv


################################################################################################################
# Set Up
## Install bandit
bandit:
	$(call execute_in_env, $(PIP) install bandit)

## Install safety
safety:
	$(call execute_in_env, $(PIP) install safety)

## Install black
black:
	$(call execute_in_env, $(PIP) install black==22.12.0)

## Install coverage
coverage:
	$(call execute_in_env, $(PIP) install coverage)

flake8:
	$(call execute_in_env, $(PIP) install flake8)


## Set up dev requirements (bandit, safety, flake8)
dev-setup: bandit safety black coverage flake8

################################################################################################################
## Test and Security

## Run set up test warehouse database
setup-db:
	$(psql -f db/db.sql)
	
## Run the security test (bandit + safety)
security-test:
	$(call execute_in_env, safety check -r ./requirements.txt -i 66742 -i 70612)
	$(call execute_in_env, bandit -lll */*.py *c/*.py)

## Run the black code check
run-black:
	$(call execute_in_env, black src test)

## Run flake8
run-flake8: dev-setup
	$(call execute_in_env, flake8  ./src/*.py ./test/*.py)

## Run the unit tests
unit-test: setup-db
	$(call execute_in_env, PYTHONPATH=${PYTHONPATH} pytest -vvvrP \
	--ignore=dependencies/python/ \
	--testdox)

## Run all tests including test_recorder.py, test_import.py
unit-test-all: setup-db
	$(call execute_in_env, PYTHONPATH=${PYTHONPATH} pytest -vvv --disable-warnings --testdox --no-summary)

## Run the coverage check
check-coverage:
	$(call execute_in_env, PYTHONPATH=${PYTHONPATH} pytest --cov=src test/)
##  $(call execute_in_env, PYTHONPATH=${PYTHONPATH} coverage run \
	# --omit=venv/* --omit=dependencies/python/ \
	# -m pytest && coverage report --omit=venv/* --omit=dependencies/python/ -m)

## Run all checks (black, security, unit tests, coverage)
run-checks:  run-black security-test unit-test check-coverage 

################################################################################################################
## Utility

## Full workflow: Clean, set up environment, run Terraform plan
plan: clean-dependencies custom-dependencies terraform-plan

## Full workflow: Clean, set up environment, apply Terraform changes
apply: clean-dependencies custom-dependencies terraform-apply

## Full workflow: Clean, set up environment, destroy Terraform infrastructure
destroy: clean-dependencies custom-dependencies terraform-destroy