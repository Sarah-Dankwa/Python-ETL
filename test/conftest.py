import pytest
import os
import boto3
from moto import mock_aws
from dotenv import load_dotenv
import json
from db.connection import connect_to_db
from unittest.mock import patch
from datetime import datetime
from db.seed import seed_warehouse


@pytest.fixture(scope="session")
def aws_credentials():
    """mock credentials for moto"""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"


@pytest.fixture
def patch_bucket_name():
    with patch("src.extract.BUCKET_NAME", "test-ingestion-bucket") as bucket:
        yield bucket


@pytest.fixture
def environment_variables():
    """load environment variables from env"""
    load_dotenv()
    yield


@pytest.fixture
def now_variable():
    with patch.object("src.extract.now", datetime(2024, 10, 15, 20, 25)) as dt:
        yield dt


@pytest.fixture
def secretsmanager_client(
    aws_credentials, environment_variables, secretsmanager_client_test
):
    """mock boto3 secretsmanager client with db credentials from local .env"""
    # load_dotenv()
    secret = {}
    secret["Database"] = os.environ["TOTESYS_DATABASE"]
    secret["Hostname"] = os.environ["TOTESYS_HOSTNAME"]
    secret["Username"] = os.environ["TOTESYS_USERNAME"]
    secret["Password"] = os.environ["TOTESYS_PASSWORD"]
    secret["Port"] = os.environ["TOTESYS_PORT"]
    json_secret = json.dumps(secret)
    with mock_aws():
        client = boto3.client("secretsmanager", region_name="eu-west-2")
        client.create_secret(Name="totesys-database", SecretString=json_secret)
        yield client


@pytest.fixture
def secretsmanager_client_test(aws_credentials):
    """mock boto3 secretsmanager client with test secret"""
    load_dotenv()
    with mock_aws():
        client = boto3.client("secretsmanager", region_name="eu-west-2")
        yield client


@pytest.fixture
def ssm_client(aws_credentials):
    """mock boto3 ssm client"""
    with mock_aws():
        yield boto3.client("ssm", region_name="eu-west-2")


@pytest.fixture
def s3_client(aws_credentials):
    """mock aws s3 client with a test ingestion and transformation bucket"""
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
    """table names in the totesys OLTP database"""
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


@pytest.fixture
def valid_warehouse_credentials(aws_credentials, environment_variables):
    """mock boto3 secretsmanager client with warehouse credentials from local
    .env"""

    secret = {}
    secret["Database"] = os.environ["LOCAL_DATABASE"]
    secret["Hostname"] = os.environ["LOCAL_HOST"]
    secret["Username"] = os.environ["LOCAL_USER"]
    secret["Password"] = os.environ["LOCAL_PASSWORD"]
    secret["Port"] = os.environ["LOCAL_PORT"]
    json_secret = json.dumps(secret)
    with mock_aws():
        client = boto3.client("secretsmanager", region_name="eu-west-2")
        client.create_secret(Name="totesys-warehouse", SecretString=json_secret)
        yield client


@pytest.fixture
def invalid_warehouse_credentials(secretsmanager_client_test):
    """invalid database connections added to mock secrets manager to test
    error handling
    """

    secret = {}
    secret["Database"] = "invalid_db"
    secret["Hostname"] = "invalid_host"
    secret["Username"] = "invalid_user"
    secret["Password"] = "invalid_password"
    secret["Port"] = "invalid_port"
    json_secret = json.dumps(secret)
    secretsmanager_client_test.create_secret(
        Name="totesys-warehouse", SecretString=json_secret
    )
    yield secretsmanager_client_test


@pytest.fixture
def conn():
    """connects to local database & adds empty tables
    
    yields a connection to the local database 
    then closes the connection after each test is complete
    """

    db = None
    try:
        db = connect_to_db()
        seed_warehouse(db)
        yield db
    finally:
        if db:
            db.close()

