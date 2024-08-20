#################################################################################
#
# Makefile to build the project
#
#################################################################################

PROJECT_NAME = password_manager
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
	rm -rf dependencies/python/*

##	@echo ">>> Installing pandas to dependencies/python..."
##	$(call execute_in_env, $(PIP) install pandas -t dependencies/python --no-cache-dir)

	@echo ">>> Installing pg8000 to dependencies/python..."
	$(call execute_in_env, $(PIP) install pg8000 -t dependencies/python --no-cache-dir)

all-requirements: requirements custom-dependencies
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
	$(call execute_in_env, PYTHONPATH=${PYTHONPATH} pytest -vvv \
	--ignore=dependencies/python/ \
	--no-summary \
	--testdox)

## Run all tests including test_recorder.py, test_import.py
unit-test-all: setup-db
	$(call execute_in_env, PYTHONPATH=${PYTHONPATH} pytest -vvv --disable-warnings --testdox --no-summary)

## Run the coverage check
check-coverage:
	$(call execute_in_env, PYTHONPATH=${PYTHONPATH} pytest --cov=src test/)
# $(call execute_in_env, PYTHONPATH=${PYTHONPATH} coverage run \
	# --omit=venv/* --omit=dependencies/python/ \
	# -m pytest && coverage report --omit=venv/* --omit=dependencies/python/ -m)



## Run all checks
run-checks:  run-black security-test unit-test check-coverage 
## 
