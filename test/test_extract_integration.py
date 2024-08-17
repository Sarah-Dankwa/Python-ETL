import pytest
from pg8000.native import Connection
from datetime import datetime
from unittest.mock import patch, call, Mock
import logging
import json
import pyarrow.parquet as pq
from src.extract import list_bucket_objects, fetch_from_db, lambda_handler


@pytest.fixture
def invalid_db_credentials(secretsmanager_client_test):
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
        Name="totesys-database", SecretString=json_secret
    )
    yield secretsmanager_client_test


@patch("src.extract.BUCKET_NAME", "test-ingestion-bucket")
class TestFetchFromDB:
    """test fetch from db function"""

    @pytest.mark.it("fetch from db calls get_table_names function")
    @patch("src.extract.get_table_names", return_value=list(range(3)))
    @patch("src.extract.get_single_table", return_value=[])
    def test_full_fetch_calls_get_table_names(
        self, mock_single_table, mock_table_names
    ):
        fetch_from_db()
        mock_table_names.assert_called()

    @pytest.mark.it("logs error if less than 11 tables")
    @patch("src.extract.get_table_names", return_value=list(range(10)))
    @patch("src.extract.get_single_table", return_value=[])
    def test_logs_error_if_too_few_tables(
        self, mock_single_table, mock_table_names, caplog
    ):
        with caplog.at_level(logging.ERROR):
            fetch_from_db()
            assert (
                "There are 10 tables fetched from the database - please check."
                in caplog.text
            )

    @pytest.mark.it("logs warning if more than 11 tables")
    @patch("src.extract.get_table_names", return_value=list(range(12)))
    @patch("src.extract.get_single_table", return_value=[])
    def test_logs_error_if_too_many_tables(
        self, mock_single_table, mock_table_names, caplog
    ):
        with caplog.at_level(logging.WARN):
            fetch_from_db()
            assert "A table has been added to the database" in caplog.text

    @pytest.mark.it("fetch from db calls get_single_table with expected arguments")
    @patch("src.extract.get_table_names")
    @patch("src.extract.get_single_table", return_value=[])
    def test_full_fetch_calls_get_single_table(
        self, mock_single_table, mock_table_names, table_names, s3_client
    ):
        mock_table_names.return_value = table_names

        expected_calls = [call(table, None) for table in table_names]
        fetch_from_db()
        assert mock_single_table.mock_calls == expected_calls

    @pytest.mark.it("info message logged for each table added")
    @patch("src.extract.get_table_names")
    @patch("src.extract.get_single_table", return_value=[{"key1": "value1"}])
    def test_full_fetch_calls_get_single_table(
        self, mock_single_table, mock_table_names, table_names, caplog, s3_client
    ):
        mock_table_names.return_value = table_names

        fetch_from_db()
        with caplog.at_level(logging.INFO):
            fetch_from_db()
            for table in table_names:
                assert f"{table} files added to s3 bucket" in caplog.text

    @pytest.mark.it("get single table is not called if less than 11 tables")
    @patch("src.extract.get_table_names", return_value=list(range(10)))
    @patch("src.extract.get_single_table", return_value=[])
    def test_single_table_not_called_when_too_few_tables(
        self, mock_single_table, mock_table_names, table_names
    ):

        fetch_from_db()
        assert not mock_single_table.called

    @pytest.mark.it("get single table is not called if more than 11 tables")
    @patch("src.extract.get_table_names", return_value=list(range(12)))
    @patch("src.extract.get_single_table", return_value=[])
    def test_single_table_not_called_when_too_many_tables(
        self, mock_single_table, mock_table_names, table_names
    ):

        fetch_from_db()
        assert not mock_single_table.called

    @pytest.mark.it("does not call convert to parquet if table is empty")
    @patch("src.extract.convert_to_parquet")
    @patch("src.extract.get_table_names", return_value=list(range(11)))
    @patch("src.extract.get_single_table", return_value=[])
    def test_does_not_call_convert_to_parquet_if_table_empty(
        self, mock_single_table, mock_table_names, mock_convert_to_parquet
    ):

        fetch_from_db()
        assert not mock_convert_to_parquet.called

    @pytest.mark.it("does not add any empty tables to bucket")
    @patch("src.extract.convert_to_parquet")
    @patch("src.extract.get_table_names", return_value=list(range(11)))
    @patch("src.extract.get_single_table", return_value=[])
    def test_does_not_add_files_to_bucket_if_files_are_empty(
        self, mock_single_table, mock_table_names, mock_convert_to_parquet, s3_client
    ):

        fetch_from_db()
        assert list_bucket_objects() == 0

    @pytest.mark.it("fetch from db adds objects to s3 bucket with expected keys")
    @patch("src.extract.year", "2024")
    @patch("src.extract.month", "10")
    @patch("src.extract.day", "15")
    @patch("src.extract.time", "20:25")
    @patch("src.extract.get_table_names")
    @patch("src.extract.get_single_table", return_value=[{"test": "test"}])
    def test_full_fetch_uploads_files_to_s3(
        self,
        mock_single_table,
        mock_table_names,
        table_names,
        s3_client,
        patch_bucket_name,
    ):
        mock_table_names.return_value = table_names
        expected_keys = [
            f"{name}/2024/10/15/20:25/{name}.parquet" for name in table_names
        ]
        fetch_from_db()
        objects = s3_client.list_objects_v2(Bucket="test-ingestion-bucket")
        returned_keys = [o["Key"] for o in objects["Contents"]]
        for key in expected_keys:
            assert key in returned_keys


class TestLambdaHandler:
    """tests from lambda handler function"""

    @pytest.mark.it("lambda_handler logs error if no connection")
    @patch("src.extract.BUCKET_NAME", "test-ingestion-bucket")
    @patch("src.extract.save_datetime_parameter")
    @patch("src.extract.list_bucket_objects", return_value=0)
    def test_lambda_handler_logs_error_if_no_connection(
        self, mock_list_objects, mock_save_parameter, invalid_db_credentials, caplog
    ):
        with caplog.at_level(logging.ERROR):
            lambda_handler()
            assert "NO CONNECTION TO DATABASE - PLEASE CHECK" in caplog.text

    @pytest.mark.it("lambda_handler logs error if no bucket variable")
    @patch("src.extract.save_datetime_parameter")
    @patch("src.extract.fetch_from_db")
    @patch("src.extract.list_bucket_objects", return_value=0)
    def test_lambda_handler_logs_error_if_no_bucket_value(
        self,
        mock_list_objects,
        mock_fetch_from_db,
        mock_save_parameter,
        secretsmanager_client,
        caplog,
    ):
        with caplog.at_level(logging.ERROR):
            lambda_handler({}, {})
            assert "BUCKET NOT FOUND - PLEASE CHECK" in caplog.text

    @pytest.mark.it("lambda_handler calls list objects function")
    @patch("src.extract.BUCKET_NAME", "test-ingestion-bucket")
    @patch("src.extract.save_datetime_parameter")
    @patch("src.extract.fetch_from_db")
    @patch("src.extract.list_bucket_objects", return_value=0)
    def test_lambda_handler_calls_list_objects_function(
        self,
        mock_list_objects,
        mock_fetch_from_db,
        mock_save_parameter,
        secretsmanager_client,
    ):
        lambda_handler({}, {})
        mock_list_objects.assert_called()

    @pytest.mark.it("when bucket is not empty retrieve datetime parameter is called")
    @patch("src.extract.BUCKET_NAME", "test-ingestion-bucket")
    @patch("src.extract.retrieve_datetime_parameter", return_value="2024-01-01")
    @patch("src.extract.list_bucket_objects", return_value=1)
    def test_lambda_handler_calls_retrieve_date_time_param(
        self, mock_list_objects, mock_date_time, s3_client, secretsmanager_client
    ):

        lambda_handler({}, {})
        mock_date_time.assert_called()

    @pytest.mark.it(
        "when bucket is empty lambda handler calls full " + "fetch with no arguments"
    )
    @patch("src.extract.save_datetime_parameter")
    @patch("src.extract.fetch_from_db")
    @patch("src.extract.list_bucket_objects", return_value=0)
    def test_lambda_handler_calls_full_fetch_with_no_args(
        self,
        mock_list_objects,
        mock_fetch_from_db,
        mock_save_parameter,
        s3_client,
        secretsmanager_client,
    ):
        lambda_handler({}, {})
        mock_fetch_from_db.assert_called_with()

    @pytest.mark.it(
        "when bucket is not empty lambda handler calls"
        + " fetch from db expected argument"
    )
    @patch("src.extract.retrieve_datetime_parameter", return_value="2024-01-01")
    @patch("src.extract.save_datetime_parameter")
    @patch("src.extract.fetch_from_db")
    @patch("src.extract.list_bucket_objects", return_value=1)
    def test_lambda_handler_calls_full_fetch_with_expected_args(
        self,
        mock_list_objects,
        mock_fetch_from_db,
        mock_save_parameter,
        mock_date_time,
        s3_client,
        secretsmanager_client,
    ):
        lambda_handler()
        mock_fetch_from_db.assert_called_with("2024-01-01")

    @pytest.mark.it("lambda handler calls save date time parameter")
    @patch("src.extract.connect_to_db", return_value=True)
    @patch("src.extract.save_datetime_parameter")
    @patch("src.extract.fetch_from_db")
    @patch("src.extract.list_bucket_objects", return_value=0)
    def test_lambda_handler_calls_save_datetime_parameter(
        self,
        mock_list_objects,
        mock_fetch_from_db,
        mock_save_parameter,
        mock_connect_to_db,
        s3_client,
        secretsmanager_client,
    ):
        lambda_handler({}, {})
        mock_save_parameter.assert_called()

    @pytest.mark.it("logs info if no tables added to database")
    @patch("src.extract.retrieve_datetime_parameter", return_value="2024-01-01")
    @patch("src.extract.save_datetime_parameter")
    @patch("src.extract.fetch_from_db", return_value=[])
    @patch("src.extract.list_bucket_objects", return_value=1)
    def test_logs_info_if_no_tables_added(
        self,
        mock_list_objects,
        mock_fetch_from_db,
        mock_save_parameter,
        s3_client,
        secretsmanager_client,
        caplog,
    ):
        with caplog.at_level(logging.INFO):
            lambda_handler({}, {})
            assert (
                "No new files have been added to the database at this stage"
                in caplog.text
            )
