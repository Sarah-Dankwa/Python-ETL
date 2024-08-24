import pytest
from unittest.mock import patch, call
from pg8000.native import Connection
import pandas as pd
import logging
from decimal import Decimal
from datetime import date, time
from botocore.exceptions import ClientError
from moto import mock_aws
import boto3
import json
from pg8000.exceptions import InterfaceError, DatabaseError
from src.load import (
    send_sns_notification,
    get_warehouse_credentials,
    get_latest_data_for_one_table,
    db_connection,
    insert_new_data_into_data_warehouse,
    lambda_handler,
)


@pytest.fixture
def mock_send_sns_func():
    with patch("src.load.send_sns_notification") as mock_func:
        yield mock_func


@pytest.fixture
def test_arn_var():
    with patch("src.load.SNS_TOPIC_ARN", "test-arn") as arn:
        return arn


@pytest.fixture
def test_bucket_var():
    with patch("src.load.BUCKET_NAME", "test-transformation-bucket") as bucket:
        yield bucket


@pytest.fixture
def bucket_with_data(s3_client):
    fact_filename = "db/transformed_data/fact_sales_order.parquet"
    fact_key = "test_file.parquet"
    bucket_name = "test-transformation-bucket"
    s3_client.upload_file(fact_filename, bucket_name, fact_key)
    yield s3_client


class TestSendSNSNotification:
    @pytest.mark.it("test sns logs arn")
    def test_sns_logs_arn(self, caplog, sns_and_topic):
        _, topic_arn = sns_and_topic

        with patch("src.load.SNS_TOPIC_ARN", topic_arn):
            with caplog.at_level(logging.INFO):
                send_sns_notification("test_message")
                assert f"SNS_TOPIC_ARN: {topic_arn}" in caplog.text

    @mock_aws
    @pytest.mark.it("test sns publishes expected message")
    def test_sns_publishes_expected_message(self, sns_and_topic, aws_credentials):
        sns, topic_arn = sns_and_topic
        sqs = boto3.client("sqs", region_name="eu-west-2")
        queue = sqs.create_queue(
            QueueName="test-queue",
        )
        queue_url = queue["QueueUrl"]
        queue_attributes = sqs.get_queue_attributes(
            QueueUrl=queue_url, AttributeNames=["QueueArn"]
        )
        queue_arn = queue_attributes["Attributes"]["QueueArn"]
        sns.subscribe(TopicArn=topic_arn, Protocol="sqs", Endpoint=queue_arn)

        test_message = "test_message"
        with patch("src.load.SNS_TOPIC_ARN", topic_arn):
            send_sns_notification(test_message)

        messages = sqs.receive_message(QueueUrl=queue_url)
        message_body = json.loads(messages["Messages"][0]["Body"])

        assert message_body["Message"] == "test_message"
        assert message_body["Subject"] == "Error in Load Lambda Function"
        assert message_body["TopicArn"] == topic_arn

    @pytest.mark.it("test sns logs error if arn not found")
    def test_sns_logs_error_if_arn_not_found(self, sns_and_topic, test_arn_var, caplog):
        with caplog.at_level(logging.INFO):
            send_sns_notification("test_message")
            assert "Failed to send SNS notification:" in caplog.text


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

    @pytest.mark.it("raises client error if secret not found")
    def test_get_database_credentials_raises_client_error(
        self, caplog, secretsmanager_client_test, mock_send_sns_func
    ):
        with pytest.raises(ClientError):
            get_warehouse_credentials()

    @pytest.mark.it("send sns notification function called if secret not found")
    def test_get_database_credentials_calls_send_sns_func(
        self, caplog, secretsmanager_client_test, mock_send_sns_func
    ):
        with pytest.raises(ClientError):
            get_warehouse_credentials()
        assert mock_send_sns_func.called

    @pytest.mark.it("logs error if secret not found")
    def test_get_database_credentials_logs_error(
        self, mock_send_sns_func, caplog, secretsmanager_client_test
    ):
        with caplog.at_level(logging.INFO):
            with pytest.raises(ClientError):
                get_warehouse_credentials()
        assert "The database [totesys-warehouse] could not be found" in caplog.text


class TestDBConnection:
    """tests for the db connection function"""

    @pytest.mark.it("Test db connection connects to database")
    def test_connection_to_db(self, valid_warehouse_credentials):
        db = db_connection()
        assert isinstance(db, Connection)

    @pytest.mark.it("error raised if unable to connect to database")
    def test_db_connection_raises_error_if_cannot_connect(
        self, mock_send_sns_func, invalid_warehouse_credentials, caplog
    ):
        with pytest.raises(InterfaceError):
            db_connection()

    @pytest.mark.it("send sns function called if unable to connect to database")
    def test_db_connection_calls_send_sns_func(
        self, mock_send_sns_func, invalid_warehouse_credentials, caplog
    ):
        with pytest.raises(InterfaceError):
            db_connection()
        assert mock_send_sns_func.called

    @pytest.mark.it("Logs an error if unable to connect to database")
    def test_logs_an_error(
        self, mock_send_sns_func, invalid_warehouse_credentials, caplog
    ):
        with caplog.at_level(logging.INFO):
            with pytest.raises(InterfaceError):
                db_connection()
        assert "No connection to database - please check:" in caplog.text


class TestGetLatestDataForOneTable:
    """tests for the get latest data for one table function"""

    @pytest.mark.it("function returns a dataframe")
    def test_function_returns_a_dataframe(self, test_bucket_var, bucket_with_data):
        key = "test_file.parquet"
        response = get_latest_data_for_one_table(key)
        assert isinstance(response, pd.DataFrame)

    @pytest.mark.it("contents of dataframe equals contents of original file")
    def test_returns_correct_contents(self, bucket_with_data, test_bucket_var):
        filename = "db/transformed_data/fact_sales_order.parquet"
        key = "test_file.parquet"
        response = get_latest_data_for_one_table(key)
        expected = pd.read_parquet(filename)
        assert response.equals(expected)

    @pytest.mark.it("raises client error when the bucket is empty")
    def test_raises_client_error_when_the_prcessed_bucket_is_empty(
        self, test_bucket_var, mock_send_sns_func, s3_client
    ):
        key = "test_file.parquet"
        with pytest.raises(ClientError):
            get_latest_data_for_one_table(key)

    @pytest.mark.it("calls send sns notification func when the bucket is empty")
    def test_sends_sns_notification_function_when_the_prcessed_bucket_is_empty(
        self, test_bucket_var, mock_send_sns_func, s3_client, caplog
    ):
        key = "test_file.parquet"
        with pytest.raises(ClientError):
            get_latest_data_for_one_table(key)
        assert mock_send_sns_func.called

    @pytest.mark.it("logs an error when the bucket is empty")
    def test_logs_an_error_when_the_prcessed_bucket_is_empty(
        self, test_bucket_var, mock_send_sns_func, s3_client, caplog
    ):
        key = "test_file.parquet"
        with caplog.at_level(logging.ERROR):
            with pytest.raises(ClientError):
                get_latest_data_for_one_table(key)
        assert (
            "Cannot access the parquet file in the processed data bucket:"
            in caplog.text
        )


class TestInsertNewDataIntoWarehouse:
    """tests for insert new data into warehouse function"""

    @pytest.mark.it("inserts correct number of rows into the database")
    def test_correct_number_of_rows_added_to_the_database(
        self,
        bucket_with_data,
        valid_warehouse_credentials,
        test_bucket_var,
        warehouse_conn,
    ):
        key = "test_file.parquet"
        df = get_latest_data_for_one_table(key)
        insert_new_data_into_data_warehouse(df, "fact_sales_order")
        response = warehouse_conn.run("SELECT * FROM fact_sales_order")
        assert len(response) == 100

    @pytest.mark.it("inserts data with the correct data types into the warehouse")
    def test_correct_data_types_inserted_into_warehouse(
        self,
        bucket_with_data,
        valid_warehouse_credentials,
        test_bucket_var,
        warehouse_conn,
    ):
        key = "test_file.parquet"
        df = get_latest_data_for_one_table(key)
        insert_new_data_into_data_warehouse(df, "fact_sales_order")
        response = warehouse_conn.run("SELECT * FROM fact_sales_order;")
        columns = [column["name"] for column in warehouse_conn.columns]
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
            int,
        ]
        for row in response:
            row_dict = dict(zip(columns, row))
            for index, key in enumerate(columns):
                assert isinstance(row_dict[key], data_types[index])

    @pytest.mark.it("does not add new rows for duplicate data in dimension table")
    def test_no_new_rows_for_duplicate_data_in_dim(
        self, bucket_with_data, valid_warehouse_credentials, warehouse_conn
    ):
        currency_data = [
            {
                "currency_id": 1,
                "currency_code": "GBP",
                "currency_name": "British pound",
            },
            {
                "currency_id": 2,
                "currency_code": "USD",
                "currency_name": "United States dollar",
            },
            {
                "currency_id": 3,
                "currency_code": "EUR",
                "currency_name": "European Euro",
            },
        ]
        df = pd.DataFrame(currency_data)
        insert_new_data_into_data_warehouse(df, "dim_currency")
        insert_new_data_into_data_warehouse(df, "dim_currency")
        response = warehouse_conn.run("SELECT * FROM dim_currency")
        assert len(response) == 3

    @pytest.mark.it("updates rows when values changed in dimension table")
    def test_updates_rows_in_dim(self, valid_warehouse_credentials, warehouse_conn):
        currency_data = [
            {
                "currency_id": 1,
                "currency_code": "GBP",
                "currency_name": "British pound",
            },
            {
                "currency_id": 2,
                "currency_code": "USD",
                "currency_name": "United States dollar",
            },
            {
                "currency_id": 3,
                "currency_code": "EUR",
                "currency_name": "European Euro",
            },
        ]
        updated_currency_data = [
            {
                "currency_id": 1,
                "currency_code": "GBP",
                "currency_name": "updated pound",
            },
            {
                "currency_id": 2,
                "currency_code": "USD",
                "currency_name": "updated dollar",
            },
            {"currency_id": 3, "currency_code": "EUR", "currency_name": "updated euro"},
        ]
        df = pd.DataFrame(currency_data)
        updated_df = pd.DataFrame(updated_currency_data)

        insert_new_data_into_data_warehouse(df, "dim_currency")
        insert_new_data_into_data_warehouse(updated_df, "dim_currency")
        response = warehouse_conn.run("SELECT currency_name FROM dim_currency")
        assert response == [["updated pound"], ["updated dollar"], ["updated euro"]]

    @pytest.mark.it("insert data raises error with empty dataframe")
    def test_insert_data_raises_error_with_empty_dataframe(
        self,
        bucket_with_data,
        valid_warehouse_credentials,
        warehouse_conn,
        mock_send_sns_func,
        caplog,
        test_bucket_var,
    ):
        df = pd.DataFrame()
        with pytest.raises(DatabaseError):
            insert_new_data_into_data_warehouse(df, "fact_sales_order")

    @pytest.mark.it("logs error with empty dataframe")
    def test_insert_data_logs_error_with_empty_dataframe(
        self,
        bucket_with_data,
        valid_warehouse_credentials,
        warehouse_conn,
        mock_send_sns_func,
        caplog,
        test_bucket_var,
    ):
        df = pd.DataFrame()
        with caplog.at_level(logging.ERROR):
            with pytest.raises(DatabaseError):
                insert_new_data_into_data_warehouse(df, "fact_sales_order")
        assert "Cannot add data to the database:" in caplog.text

    @pytest.mark.it("calls send sns func with empty dataframe")
    def test_insert_data_calls_sns_func_with_empty_dataframe(
        self,
        bucket_with_data,
        valid_warehouse_credentials,
        warehouse_conn,
        mock_send_sns_func,
        caplog,
        test_bucket_var,
    ):
        df = pd.DataFrame()
        with pytest.raises(DatabaseError):
            insert_new_data_into_data_warehouse(df, "fact_sales_order")
        assert mock_send_sns_func.called

    @pytest.mark.it("raises database error invalid table name")
    def test_raises_db_error_with_invalid_table_name(
        self,
        bucket_with_data,
        valid_warehouse_credentials,
        test_bucket_var,
        warehouse_conn,
        mock_send_sns_func,
        caplog,
    ):
        key = "test_file.parquet"
        df = get_latest_data_for_one_table(key)
        with pytest.raises(DatabaseError):
            insert_new_data_into_data_warehouse(df, "invalid_table")

    @pytest.mark.it("logs error with invalid table name")
    def test_insert_data_logs_error_with_invalid_table_name(
        self,
        bucket_with_data,
        valid_warehouse_credentials,
        warehouse_conn,
        mock_send_sns_func,
        caplog,
        test_bucket_var,
    ):
        key = "test_file.parquet"
        df = get_latest_data_for_one_table(key)
        with caplog.at_level(logging.ERROR):
            with pytest.raises(DatabaseError):
                insert_new_data_into_data_warehouse(df, "invalid_table")
        assert "Cannot add data to the database:" in caplog.text

    @pytest.mark.it("calls send sns func with invalid table name")
    def test_insert_data_calls_sns_func_with_invalid_table_name(
        self,
        bucket_with_data,
        valid_warehouse_credentials,
        warehouse_conn,
        mock_send_sns_func,
        caplog,
        test_bucket_var,
    ):
        key = "test_file.parquet"
        df = get_latest_data_for_one_table(key)
        with pytest.raises(DatabaseError):
            insert_new_data_into_data_warehouse(df, "invalid_table_name")
        assert mock_send_sns_func.called


class TestLambdaHandler:
    """tests for the lambda handler"""

    @pytest.mark.it("calls get_latest_data_for_one_table for every key in event")
    @patch("src.load.insert_new_data_into_data_warehouse")
    @patch("src.load.get_latest_data_for_one_table", return_value=pd.DataFrame)
    def test_calls_get_latest_data_for_every_key_in_event(
        self, mock_get_data, mock_insert_data, valid_warehouse_credentials, s3_client
    ):
        test_event = ["key1", "key2", "key3"]
        lambda_handler(test_event, None)
        for key in test_event:
            assert call(key) in mock_get_data.mock_calls

    @pytest.mark.it("if dataframe is not returned insert new data not called")
    @patch("src.load.insert_new_data_into_data_warehouse")
    @patch("src.load.get_latest_data_for_one_table", return_value=None)
    def test_insert_data_not_called_if_no_data(
        self, mock_get_data, mock_insert_data, valid_warehouse_credentials, s3_client
    ):
        test_event = ["key1", "key2", "key3"]
        lambda_handler(test_event, None)
        mock_insert_data.assert_not_called

    @pytest.mark.it("calls insert new data with the correct table name")
    @patch("src.load.insert_new_data_into_data_warehouse")
    @patch("src.load.get_latest_data_for_one_table", return_value="test")
    def test_uses_the_correct_table_name(
        self, mock_get_data, mock_insert_data, valid_warehouse_credentials, s3_client
    ):
        test_event = [
            "dim_date/2024/08/21/11:32:21/dim_date.parquet",
            "fact_sales_order/2024/08/21/11:32:21/fact_sales_order.parquet",
        ]
        lambda_handler(test_event, None)
        assert call("test", "dim_date") in mock_insert_data.mock_calls
        assert call("test", "fact_sales_order") in mock_insert_data.mock_calls

    @pytest.mark.it("logs info when table added to data warehouse")
    @patch("src.load.insert_new_data_into_data_warehouse")
    @patch("src.load.get_latest_data_for_one_table", return_value="test")
    def test_logs_info_when_data_added_to_the_warehouse(
        self,
        mock_get_data,
        mock_insert_data,
        valid_warehouse_credentials,
        s3_client,
        caplog,
    ):
        test_event = [
            "dim_date/2024/08/21/11:32:21/dim_date.parquet",
            "fact_sales_order/2024/08/21/11:32:21/fact_sales_order.parquet",
        ]
        with caplog.at_level(logging.INFO):
            lambda_handler(test_event, None)
        assert "Data added to the dim_date table in the data warehouse." in caplog.text
        assert (
            "Data added to the fact_sales_order table in the data warehouse."
            in caplog.text
        )

    @pytest.mark.it("raises error with invalid test_event")
    def test_raises_exception_for_invalid_test_event(
        self,
        s3_client,
        valid_warehouse_credentials,
        test_bucket_var,
        warehouse_conn,
        mock_send_sns_func,
        caplog,
    ):
        with pytest.raises(Exception):
            lambda_handler(3, None)

    @pytest.mark.it("logs error with invalid test event")
    def test_logs_error_for_invalid_test_event(
        self,
        s3_client,
        valid_warehouse_credentials,
        warehouse_conn,
        mock_send_sns_func,
        caplog,
        test_bucket_var,
    ):
        with caplog.at_level(logging.ERROR):
            with pytest.raises(Exception):
                lambda_handler(3, None)
        assert "Error Type: TypeError" in caplog.text

    @pytest.mark.it("calls send sns func with invalid event")
    def test_insert_data_calls_sns_func_with_invalid_event(
        self,
        s3_client,
        valid_warehouse_credentials,
        warehouse_conn,
        mock_send_sns_func,
        caplog,
        test_bucket_var,
    ):

        with pytest.raises(Exception):
            lambda_handler(3, None)
        assert mock_send_sns_func.called
