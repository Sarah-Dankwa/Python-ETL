import pytest
import os
import boto3
from moto import mock_aws
from pg8000.native import Connection
from dotenv import load_dotenv
import json
from unittest.mock import patch
from datetime import datetime


@pytest.fixture(scope='session')
def aws_credentials():
    '''mock credentials for moto'''
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'eu-west-2'


@pytest.fixture
def patch_bucket_name():
    with patch("src.extract.BUCKET_NAME", "test-ingestion-bucket") as bucket:
        yield bucket

@pytest.fixture
def environment_variables():
    '''load environment variables from env'''
    load_dotenv()
    yield

@pytest.fixture
def now_variable():
    with patch.object('src.extract.now', datetime(2024, 10, 15, 20, 25)) as dt:
        yield dt

@pytest.fixture
def secretsmanager_client(aws_credentials, environment_variables):
    '''mock boto3 secretsmanager client with db credentials from local .env'''
    #load_dotenv()
    secret = {}
    secret['Database'] = os.environ['TOTESYS_DATABASE']
    secret['Hostname'] = os.environ['TOTESYS_HOSTNAME']
    secret['Username'] = os.environ['TOTESYS_USERNAME']
    secret['Password'] = os.environ['TOTESYS_PASSWORD']
    secret['Port'] = os.environ['TOTESYS_PORT']
    json_secret = json.dumps(secret)
    with mock_aws():
        client =  boto3.client("secretsmanager", region_name="eu-west-2")
        client.create_secret(
            Name="totesys-database", SecretString=json_secret
        )
        yield client

@pytest.fixture
def secretsmanager_client_test(aws_credentials):
    '''mock boto3 secretsmanager client with test secret'''
    load_dotenv()
    with mock_aws():
        client =  boto3.client("secretsmanager", region_name="eu-west-2")
        yield client


@pytest.fixture
def ssm_client(aws_credentials):
    '''mock boto3 ssm client'''
    with mock_aws():
        yield boto3.client("ssm", region_name="eu-west-2")


@pytest.fixture
def s3_client(aws_credentials):
    '''mock aws s3 client with a test ingestion and transformation bucket'''
    with mock_aws():
        client = boto3.client("s3")
        client.create_bucket(
            Bucket="test-ingestion-bucket",
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
        )
        client.create_bucket(
            Bucket="test-transformation-bucket",
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
        )
        yield client


@pytest.fixture
def table_names():
    tables = [
        "address",
        "staff",
        "payment",
        "department",
        "transaction",
        "currency",
        "payment_type",
        "sales_order",
        "counterparty",
        "purchase_order",
        "design",
    ]
    return tables

        
