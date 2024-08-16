import pytest
from pg8000.native import Connection
from datetime import datetime
from unittest.mock import patch, call
import logging
import json
import pyarrow.parquet as pq
from src.extract import (
    get_database_credentials,
    connect_to_db,
    get_single_table,
    convert_to_parquet,
    get_table_names,
    save_datetime_parameter,
    retrieve_datetime_parameter,
    list_bucket_objects,
    fetch_from_db,
    lambda_handler
)

@pytest.fixture
def invalid_db_credentials(secretsmanager_client_test):
    '''invalid database connections added to mock secrets manager to test 
    error handling
    '''

    secret = {}
    secret['Database'] = 'invalid_db'
    secret['Hostname'] = 'invalid_host'
    secret['Username'] = 'invalid_user'
    secret['Password'] = 'invalid_password'
    secret['Port'] = 'invalid_port'
    json_secret = json.dumps(secret)
    secretsmanager_client_test.create_secret(
        Name="totesys-database", SecretString=json_secret
    )
    yield secretsmanager_client_test

@pytest.mark.skip
class TestGetDatabaseCredentials:
    '''tests for get database credentials function'''

    @pytest.mark.it("get database credentials returns a dictionary")
    def test_get_database_credentials_returns_a_dictionary(
        self, 
        secretsmanager_client
    ):

        response = get_database_credentials()
        assert isinstance(response, dict)


    @pytest.mark.it("logs error if secret not found")
    def test_get_database_credentials_returns_expected(
        self, 
        secretsmanager_client_test
    ):
        secretsmanager_client_test.create_secret(
            Name="totesys-database", SecretString='{"key": "value2"}'
        )
        response = get_database_credentials()
        assert response == {"key": "value2"}


    @pytest.mark.xfail(reason='accessing secret after except')
    @pytest.mark.it("get database credentials logs error if secret not found")
    def test_get_database_credentials_logs_error(
        self, 
        caplog,
        secretsmanager_client_test
    ):
        with caplog.at_level(logging.INFO):
            get_database_credentials()
            assert "The database [totesys-database] could not be found" in caplog.text

@pytest.mark.skip
class TestDatabaseCredsAndConnection:
    '''test database connection function'''
    @pytest.mark.it("Test db connection connects to database")
    def test_connection_to_db(self, secretsmanager_client):
        db = connect_to_db()
        assert isinstance(db, Connection)

@pytest.mark.skip
class TestGetSingleTable:
    '''test get single table function'''

    @pytest.mark.it("Test returns a list of dictionaries")
    def test_returns_list_of_dictionaries(self, secretsmanager_client):
        results = get_single_table("payment_type")
        assert isinstance(results, list)
        for item in results:
            assert isinstance(item, dict)

    @pytest.mark.it("Test returns correct keys for payment type table")
    def test_returns_expected_keys(self, secretsmanager_client):
        results = get_single_table("payment_type")
        assert "payment_type_id" in results[0]
        assert "payment_type_name" in results[0]
        assert "created_at" in results[0]
        assert "last_updated" in results[0]

    @pytest.mark.it("when given date only returns entries after given date")
    def test_filters_table_by_given_date(self, secretsmanager_client):
        sample_date = datetime(2022, 10, 20)
        results = get_single_table("sales_order", sample_date)
        for row in results:
            assert row["last_updated"] > sample_date

    @pytest.mark.it("logs error if table not found")
    def test_logs_error_with_invalid_table(self, secretsmanager_client, caplog):
        with caplog.at_level(logging.INFO):
            get_single_table("table_not_in_db")
            assert "Database or Client error:" in caplog.text
            assert 'relation "table_not_in_db" does not exist' in caplog.text

    
    @pytest.mark.xfail(reason='raises interface error')
    @pytest.mark.it("logs error if incorrect credentials")
    def test_logs_error_with_invalid_db(self, invalid_db_credentials, caplog):
        
        with caplog.at_level(logging.INFO):
            get_single_table("sales_order")
            assert "Database or Client error:" in caplog.text

@pytest.mark.skip
class TestConvertToParquet:
    @pytest.mark.it("convert to parquet saves files to a parquet format")
    def test_convert_to_parquet_saves_to_parquet_format(self, tmp_path):
        tmp_dir = tmp_path / "temp"
        tmp_dir.mkdir()
        sample_filename = tmp_dir / "sample.parquet"
        sample_table = [{"key1": "val1"}, {"key1": "val2"}]
        convert_to_parquet(sample_table, sample_filename)
        temp = pq.read_table(sample_filename).to_pylist()
        assert temp == [{"key1": "val1"}, {"key1": "val2"}]

@pytest.mark.skip
class TestGetTableNames:
    '''testing get table names function'''

    @pytest.mark.it("table names retrieves list of table names")
    def test_table_names_gets_list_of_table_names(self, secretsmanager_client, table_names):
        expected = table_names
        result = get_table_names() 
        assert result == expected


    @pytest.mark.xfail(reason='raises interface error')
    @pytest.mark.it("table names retrieves list of table names")
    def test_table_names_gets_list_of_table_names(
        self, 
        invalid_db_credentials,
        caplog,
        table_names
    ):
        
        with caplog.at_level(logging.ERROR):
            lambda_handler()
            assert "NO CONNECTION TO DATABASE - PLEASE CHECK" in caplog.text

@pytest.mark.skip
class TestRetrieveDateTimeParameter:
    '''test retrieve date time parameter function'''

    @pytest.mark.it("retrieves parameter from ssm parameter store")
    def test_retrieves_parameter_from_ssm_parameter_store(self, ssm_client):
        ssm_client.put_parameter(Name="latest-extract", Type="String", Value="test")
        assert retrieve_datetime_parameter() == "test"

    @pytest.mark.it("logs error if parameter not found")
    def test_logs_error_if_parameter_not_found(self, ssm_client, caplog):
        with caplog.at_level(logging.INFO):
            retrieve_datetime_parameter()
            assert "Could not retrieve date parameter:" in caplog.text

@pytest.mark.skip
class TestSaveDateTimeParameter:
    '''test dave date time paramenter function'''

    @pytest.mark.it("saves parameter to ssm parameter store")
    def test_saves_parameter_to_ssm_parameter_store(self, ssm_client):
        save_datetime_parameter("hello")
        assert retrieve_datetime_parameter() == "hello"

@pytest.mark.skip
@patch("src.extract.BUCKET_NAME", "test-ingestion-bucket")
class TestListBucketObjects:
    @pytest.mark.it("returns 0 when no objects in bucket")
    def test_returns_0_for_empty_bucket(self, s3_client):
        assert list_bucket_objects() == 0

    @pytest.mark.it("returns number of objects when objects in bucket")
    def test_returns_1_for_1_item_in_bucket(self, s3_client):
        s3_client.put_object(Bucket="test-ingestion-bucket", Body="hello", Key="test.txt")
        assert list_bucket_objects() == 1

@pytest.mark.skip
@patch("src.extract.BUCKET_NAME", "test-ingestion-bucket")
class TestFetchFromDB:
    '''test fetch from db function'''
    @pytest.mark.it("fetch from db calls get_table_names function")
    @patch("src.extract.get_table_names", return_value=list(range(3)))
    @patch("src.extract.get_single_table", return_value=[])
    def test_full_fetch_calls_get_table_names(
        self, 
        mock_single_table, 
        mock_table_names
    ):
        fetch_from_db()
        mock_table_names.assert_called()


    @pytest.mark.it("logs error if less than 11 tables")
    @patch("src.extract.get_table_names", return_value=list(range(10)))
    @patch("src.extract.get_single_table", return_value=[])
    def test_logs_error_if_too_few_tables(
        self, 
        mock_single_table, 
        mock_table_names,
        caplog
    ):
        with caplog.at_level(logging.ERROR):
            fetch_from_db()
            assert "There is a table missing from the database" in caplog.text
        

    @pytest.mark.it("logs warning if more than 11 tables")
    @patch("src.extract.get_table_names", return_value=list(range(12)))
    @patch("src.extract.get_single_table", return_value=[])
    def test_logs_error_if_too_many_tables(
        self, 
        mock_single_table, 
        mock_table_names,
        caplog
    ):
        with caplog.at_level(logging.WARN):
            fetch_from_db()
            assert "A table has been added to the database" in caplog.text


    @pytest.mark.it("fetch from db calls get_single_table with expected arguments")
    @patch("src.extract.get_table_names")
    @patch("src.extract.get_single_table", return_value=[])
    def test_full_fetch_calls_get_single_table(
        self, 
        mock_single_table, 
        mock_table_names, 
        table_names,
        s3_client
    ):
        mock_table_names.return_value = table_names

        expected_calls = [call(table, None) for table in table_names]
        fetch_from_db()
        assert mock_single_table.mock_calls == expected_calls


    @pytest.mark.it("info message logged for each table added")
    @patch("src.extract.get_table_names")
    @patch("src.extract.get_single_table", return_value=[{'key1': 'value1'}])
    def test_full_fetch_calls_get_single_table(
        self, 
        mock_single_table, 
        mock_table_names, 
        table_names,
        caplog,
        s3_client
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
        self, mock_single_table, 
        mock_table_names, 
        table_names
    ):
        
        fetch_from_db()
        assert not mock_single_table.called


    @pytest.mark.it("get single table is not called if more than 11 tables")
    @patch("src.extract.get_table_names", return_value=list(range(12)))
    @patch("src.extract.get_single_table", return_value=[])
    def test_single_table_not_called_when_too_many_tables(
        self, mock_single_table, 
        mock_table_names, 
        table_names
    ):
        
        fetch_from_db()
        assert not mock_single_table.called


    @pytest.mark.it("does not call convert to parquet if table is empty")
    @patch("src.extract.convert_to_parquet")
    @patch("src.extract.get_table_names", return_value=list(range(11)))
    @patch("src.extract.get_single_table", return_value=[])
    def test_does_not_call_convert_to_parquet_if_table_empty(
        self, 
        mock_single_table, 
        mock_table_names, 
        mock_convert_to_parquet
    ):
        
        fetch_from_db()
        assert not mock_convert_to_parquet.called


    @pytest.mark.it("does not add any empty tables to bucket")
    @patch("src.extract.convert_to_parquet")
    @patch("src.extract.get_table_names", return_value=list(range(11)))
    @patch("src.extract.get_single_table", return_value=[])
    def test_does_not_add_files_to_bucket_if_files_are_empty(
        self, 
        mock_single_table, 
        mock_table_names, 
        mock_convert_to_parquet,
        s3_client
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
        patch_bucket_name
    ):
        mock_table_names.return_value = table_names
        expected_keys = [
            f'{name}/2024/10/15/20:25/{name}.parquet' for name in table_names
        ]
        fetch_from_db()
        objects = s3_client.list_objects_v2(Bucket="test-ingestion-bucket")
        returned_keys = [o["Key"] for o in objects["Contents"]]
        for key in expected_keys:
            assert key in returned_keys


class TestLambdaHandler:
    '''tests from lambda handler function'''

    @pytest.mark.xfail(reason='unbound error in get_db_creds func')
    @pytest.mark.it("lambda_handler logs error if no connection")
    @patch("src.extract.BUCKET_NAME", "test-ingestion-bucket")
    @patch("src.extract.save_datetime_parameter")
    @patch("src.extract.fetch_from_db")
    @patch("src.extract.list_bucket_objects", return_value=0)
    def test_lambda_handler_logs_error_if_no_connection(
        self, 
        mock_list_objects, 
        mock_fetch_from_db, 
        mock_save_parameter,
        invalid_db_credentials,
        caplog
    ):
        with caplog.at_level(logging.ERROR):
            lambda_handler({}, {})
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
        caplog
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
        secretsmanager_client
    ):
        lambda_handler({}, {})
        mock_list_objects.assert_called()

    
    @pytest.mark.it("when bucket is not empty retrieve datetime parameter is called")
    @patch("src.extract.BUCKET_NAME", "test-ingestion-bucket")
    @patch("src.extract.retrieve_datetime_parameter", return_value="2024-01-01")
    @patch("src.extract.list_bucket_objects", return_value=1)
    def test_lambda_handler_calls_retrieve_date_time_param(
        self,
        mock_list_objects,
        mock_date_time,
        s3_client,
        secretsmanager_client
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
        self, mock_list_objects, mock_fetch_from_db, mock_save_parameter, s3_client, secretsmanager_client
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
        secretsmanager_client
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
        secretsmanager_client
    ):
        lambda_handler({}, {})
        mock_save_parameter.assert_called()

    
    @pytest.mark.it("logs info if no tables added to database")
    @patch("src.extract.retrieve_datetime_parameter", return_value='2024-01-01')
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
        caplog
    ):
        with caplog.at_level(logging.INFO):
            lambda_handler({}, {})
            assert "No new files have been added to the database at this stage" in caplog.text
