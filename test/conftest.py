import pytest
import os
import boto3
from moto import mock_aws
from pg8000.native import Connection


@pytest.fixture(scope='session')
def aws_credentials():
    '''mock credentials for moto'''
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'eu-west-2'


@pytest.fixture
def secretsmanager_client(aws_credentials):
    '''mock boto3 secretsmanager client'''
    with mock_aws():
        yield boto3.client("secretsmanager", region_name="eu-west-2")


@pytest.fixture
def ssm_client(aws_credentials):
    '''mock boto3 ssm client'''
    with mock_aws():
        yield boto3.client("ssm", region_name="eu-west-2")


@pytest.fixture
def s3_client(aws_credentials):
    '''mock aws s3 client with onne s3 bucket called test-bucket'''
    with mock_aws():
        client = boto3.client("s3")
        client.create_bucket(
            Bucket="test-bucket",
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
        )
        yield client



        
