import pytest
from dotenv import load_dotenv
from unittest.mock import patch
from pg8000.native import Connection
import pandas as pd
from db.seed import seed_warehouse
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
    lambda_handler
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


@pytest.fixture
def set_environment_variables():
    """loads environment variables to be used in tests"""
    load_dotenv()


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


class TestGetWarehouseCredentials:
    """tests for the get warehouse credentials function"""

    @pytest.mark.it("returns a dictionary")
    def test_warehouse_credentials_returns_a_dictionary(
        self, valid_warehouse_credentials
    ):
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
            assert "The database [totesys-warehouse] could not be found" in caplog.text


class TestDBConnection:
    """tests for the db connection function"""

    @pytest.mark.it("Test db connection connects to database")
    def test_connection_to_db(self, secretsmanager_client):
        db = connect_to_db()
        assert isinstance(db, Connection)

    @pytest.mark.it("Logs an error if unable to connect to database")
    def test_logs_an_error(self, invalid_warehouse_credentials, caplog):
        with caplog.at_level(logging.INFO):
            db_connection()
            assert "NO CONNECTION TO DATABASE - PLEASE CHECK" in caplog.text


class TestGetLatestDataForOneTable:
    """tests for the get latest data for one table function"""

    @pytest.mark.it("function returns a dataframe")
    @patch('src.load.BUCKET_NAME', 'test-transformation-bucket')
    def test_function_returns_a_dataframe(self, s3_client):
        filename = 'db/data/fact_sales_order.parquet'
        key = 'test_file.parquet'
        bucket_name = "test-transformation-bucket"
        s3_client.upload_file(filename, bucket_name, key)
        response = get_latest_data_for_one_table(key)
        assert isinstance(response, pd.DataFrame)


    @pytest.mark.it("contents of dataframe equals contents of original file")
    @patch('src.load.BUCKET_NAME', 'test-transformation-bucket')
    def test_returns_correct_contents(self, s3_client):
        filename = 'db/data/fact_sales_order.parquet'
        key = 'test_file.parquet'
        bucket_name = "test-transformation-bucket"
        s3_client.upload_file(filename, bucket_name, key)
        response = get_latest_data_for_one_table(key)
        expected = pd.read_parquet(filename)
        assert response.equals(expected)


class TestInsertNewDataIntoWarehouse:
    """tests for insert new data into warehouse function"""

    @pytest.mark.it("inserts data into warehouse")
    @patch('src.load.BUCKET_NAME', 'test-transformation-bucket')
    def test_data_is_inserted_into_warehouse(self, s3_client, valid_warehouse_credentials, conn):
        filename = 'db/data/fact_sales_order.parquet'
        key = 'test_file.parquet'
        bucket_name = "test-transformation-bucket"
        s3_client.upload_file(filename, bucket_name, key)
        df = get_latest_data_for_one_table(key)
        insert_new_data_into_data_warehouse(df, 'fact_sales_order')
        response = conn.run('SELECT * FROM fact_sales_order LIMIT 5')


class TestLambdaHandler:
    """tests for the lambda handler"""

    pass
