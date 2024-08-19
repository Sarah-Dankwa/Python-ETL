import pytest
from dotenv import load_dotenv
from unittest.mock import patch
from pg8000.native import Connection
from db.seed import seed
import json
import boto3
from moto import mock_aws
from db.connection import connect_to_db
import os
import logging
from src.load import (
    get_warehouse_credentials,
    get_latest_data_for_one_table,
    db_connection,
    insert_new_data_into_data_warehouse,
    lambda_handler,
)

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


@pytest.fixture(autouse=True)
def set_environment_variables():
    """loads environment variables to be used in tests"""
    load_dotenv()


@pytest.fixture()
def run_seed():
    """Runs seed before starting tests"""
    seed()


class TestGetWarehouseCredentials:
    """tests for the get warehouse credentials function"""

    @pytest.mark.it("returns a dictionary")
    def test_warehouse_credentials_returns_a_dictionary(self, valid_warehouse_credentials):

        response = get_warehouse_credentials()
        assert isinstance(response, dict)

    @pytest.mark.it("returns expected secret")
    def test_get_warehouse_credentials_returns_expected(
        self, secretsmanager_client_test
    ):
        secretsmanager_client_test.create_secret(
            Name="totesys-warehouse", SecretString='{"key": "value2"}'
        )
        response = get_warehouse_credentials()
        assert response == {"key": "value2"}

    @pytest.mark.it("logs error if secret not found")
    def test_get_database_credentials_logs_error(
        self, caplog, secretsmanager_client_test
    ):
        with caplog.at_level(logging.INFO):
            get_warehouse_credentials()
            print('print >> ', caplog.text)
            assert "The database [totesys-warehouse] could not be found" in caplog.text


class TestGetLatestDataForOneTable:
    """tests for the get latest data for one table function"""

    @pytest.mark.skip("need a test parquet file to ")
    @pytest.mark.it("function returns a list of dictionaries")
    def test_function_returns_a_list_of_dictionaries(self, s3_client):
        pass


class TestDBConnection:
    """tests for the db connection function"""

    @pytest.mark.skip
    @pytest.mark.it("Test db connection connects to database")
    def test_connection_to_db(self, valid_warehouse_credentials):
        pass


class TestInsertNewDataIntoWarehouse:
    """tests for insert new data into warehouse function"""

    @pytest.mark.skip
    @pytest.mark.it("inserts data into warehouse")
    def test_data_is_inserted_into_warehouse(self):
        pass


class TestLambdaHandler:
    """tests for the lambda handler"""

    pass
