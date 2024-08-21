import pytest
from unittest.mock import patch, call
from pg8000.native import Connection
import pandas as pd
import logging
from decimal import Decimal
from datetime import date, time
from src.load import (
    get_warehouse_credentials,
    get_latest_data_for_one_table,
    db_connection,
    insert_new_data_into_data_warehouse,
    lambda_handler
)


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
    def test_connection_to_db(
        self, valid_warehouse_credentials
    ):
        db = db_connection()
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


    @pytest.mark.it('logs an error when the bucket is empty')
    @patch('src.load.BUCKET_NAME', 'test-transformation-bucket')
    def test_logs_an_error_when_the_prcessed_bucket_is_empty(
        self, s3_client, caplog
    ):
        key = 'test_file.parquet'
        with caplog.at_level(logging.ERROR):
            get_latest_data_for_one_table(key)
            assert 'Cannot access the parquet file in the processed data bucket:' in caplog.text


class TestInsertNewDataIntoWarehouse:
    """tests for insert new data into warehouse function"""


    @pytest.mark.it("inserts correct number of rows into the database")
    @patch('src.load.BUCKET_NAME', 'test-transformation-bucket')
    def test_correct_number_of_rows_added_to_the_database(
        self, s3_client, valid_warehouse_credentials, conn
    ):
        filename = 'db/data/fact_sales_order.parquet'
        key = 'test_file.parquet'
        bucket_name = "test-transformation-bucket"
        s3_client.upload_file(filename, bucket_name, key)
        df = get_latest_data_for_one_table(key)
        insert_new_data_into_data_warehouse(df, 'fact_sales_order')
        response = conn.run('SELECT * FROM fact_sales_order')
        assert len(response) == 100


    @pytest.mark.it("inserts data with the correct data types into the warehouse")
    @patch('src.load.BUCKET_NAME', 'test-transformation-bucket')
    def test_correct_data_types_inserted_into_warehouse(self, s3_client, valid_warehouse_credentials, conn):
        filename = 'db/data/fact_sales_order.parquet'
        key = 'test_file.parquet'
        bucket_name = "test-transformation-bucket"
        s3_client.upload_file(filename, bucket_name, key)
        df = get_latest_data_for_one_table(key)
        insert_new_data_into_data_warehouse(df, 'fact_sales_order')
        response = conn.run('SELECT * FROM fact_sales_order;')
        columns = [column['name'] for column in conn.columns]
        data_types = [
            int, 
            int, 
            date, 
            time, 
            date, 
            time, 
            int, 
            int, 
            int, 
            Decimal,
            int,
            int,
            date,
            date,
            int
        ]
        for row in response:
            row_dict = dict(zip(columns, row))
            for index, key in enumerate(columns):
                assert isinstance(row_dict[key], data_types[index])


    @pytest.mark.it("logs error with empty dataframe")
    @patch('src.load.BUCKET_NAME', 'test-transformation-bucket')
    def test_logs_error_with_empty_dataframe(
        self, s3_client, valid_warehouse_credentials, conn, caplog
    ):
        df = pd.DataFrame()
        with caplog.at_level(logging.ERROR):
            insert_new_data_into_data_warehouse(df, 'fact_sales_order')
            assert 'Cannot add data to the database:' in caplog.text


    @pytest.mark.it("logs error with invalid table name")
    @patch('src.load.BUCKET_NAME', 'test-transformation-bucket')
    def test_logs_error_with_invalid_table_name(
        self, s3_client, valid_warehouse_credentials, conn, caplog
    ):
        df = pd.DataFrame()
        with caplog.at_level(logging.ERROR):
            insert_new_data_into_data_warehouse(df, 'invalid_table')
            assert 'Cannot add data to the database:' in caplog.text


@pytest.mark.skip
class TestLambdaHandler:
    """tests for the lambda handler"""
    @pytest.mark.it('calls get_latest_data_for_one_table for every key in event')
    @patch('src.load.insert_new_data_into_data_warehouse')
    @patch('src.load.get_latest_data_for_one_table', return_value=pd.DataFrame)
    def test_calls_get_latest_data_for_every_key_in_event(
        self, mock_get_data, mock_insert_data, valid_warehouse_credentials, s3_client
    ):
        test_event = ['key1', 'key2', 'key3']
        lambda_handler(test_event, None)
        for key in test_event:
            assert call(key) in mock_get_data.mock_calls


    @pytest.mark.it('if dataframe is not returned insert new data not called')
    @patch('src.load.insert_new_data_into_data_warehouse')
    @patch('src.load.get_latest_data_for_one_table', return_value=None)
    def test_insert_data_not_called_if_no_data(
        self, mock_get_data, mock_insert_data, valid_warehouse_credentials, s3_client
    ):
        test_event = ['key1', 'key2', 'key3']
        lambda_handler(test_event, None)
        mock_insert_data.assert_not_called

    
    @pytest.mark.it('calls insert new data with the correct table name')
    @patch('src.load.insert_new_data_into_data_warehouse')
    @patch('src.load.get_latest_data_for_one_table', return_value='test')
    def test_uses_the_correct_table_name(
        self, mock_get_data, mock_insert_data, valid_warehouse_credentials, s3_client
    ):
        test_event = [
            'dim_date/2024/08/21/11:32:21/dim_date.parquet',
            'fact_sales_order/2024/08/21/11:32:21/fact_sales_order.parquet'
        ]
        lambda_handler(test_event, None)
        assert call('test', 'dim_date') in mock_insert_data.mock_calls
        assert call('test', 'fact_sales_order') in mock_insert_data.mock_calls

