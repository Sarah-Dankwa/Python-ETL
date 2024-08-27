import pytest
from pg8000.native import Connection
from datetime import datetime
from unittest.mock import patch
import logging
import json
import pyarrow.parquet as pq
from db.seed import seed_oltp
from src.extract import (
    get_database_credentials,
    connect_to_db,
    get_single_table,
    convert_to_parquet,
    get_table_names,
    save_datetime_parameter,
    retrieve_datetime_parameter,
    list_bucket_objects,
)


@pytest.fixture
def oltp_db():
    """connects to local database & adds tables with oltp data

    yields a connection to the local database
    then closes the connection
    """

    db = None
    try:
        db = connect_to_db()
        seed_oltp(db)
        yield db
    finally:
        if db:
            db.close()


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


class TestGetDatabaseCredentials:
    """tests for get database credentials function"""

    @pytest.mark.it("get database credentials returns a dictionary")
    def test_get_database_credentials_returns_a_dictionary(self, secretsmanager_client):

        response = get_database_credentials()
        assert isinstance(response, dict)

    @pytest.mark.it("logs error if secret not found")
    def test_get_database_credentials_returns_expected(
        self, secretsmanager_client_test
    ):
        secretsmanager_client_test.create_secret(
            Name="totesys-database", SecretString='{"key": "value2"}'
        )
        response = get_database_credentials()
        assert response == {"key": "value2"}

    @pytest.mark.it("get database credentials logs error if secret not found")
    def test_get_database_credentials_logs_error(
        self, caplog, secretsmanager_client_test
    ):
        with caplog.at_level(logging.INFO):
            get_database_credentials()
            assert "The database [totesys-database] could not be found" in caplog.text


class TestDatabaseCredsAndConnection:
    """test database connection function"""

    @pytest.mark.it("Test db connection connects to database")
    def test_connection_to_db(self, secretsmanager_client):
        db = connect_to_db()
        assert isinstance(db, Connection)


class TestGetSingleTable:
    """test get single table function"""

    @pytest.mark.it("Test returns a list of dictionaries")
    def test_returns_list_of_dictionaries(self, secretsmanager_client, oltp_db):
        results = get_single_table("payment_type")
        assert isinstance(results, list)
        for item in results:
            assert isinstance(item, dict)

    @pytest.mark.it("Test returns correct keys for payment type table")
    def test_returns_expected_keys(self, secretsmanager_client, oltp_db):
        results = get_single_table("payment_type")
        assert "payment_type_id" in results[0]
        assert "payment_type_name" in results[0]
        assert "created_at" in results[0]
        assert "last_updated" in results[0]

    @pytest.mark.it("when given date only returns entries after given date")
    def test_filters_table_by_given_date(self, secretsmanager_client, oltp_db):
        sample_date = datetime(2022, 10, 20)
        results = get_single_table("sales_order", sample_date)
        for row in results:
            assert row["last_updated"] > sample_date

    @pytest.mark.it("logs error if table not found")
    def test_logs_error_with_invalid_table(
        self, caplog, secretsmanager_client, oltp_db
    ):
        with caplog.at_level(logging.INFO):
            get_single_table("table_not_in_db")
            assert 'relation "table_not_in_db" does not exist' in caplog.text

    @pytest.mark.it("logs error if incorrect credentials")
    def test_logs_error_with_invalid_db(self, invalid_db_credentials, caplog):

        with caplog.at_level(logging.ERROR):
            get_single_table("sales_order")
            assert "NO CONNECTION TO DATABASE - PLEASE CHECK" in caplog.text


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


@patch("src.extract.BUCKET_NAME", "test-ingestion-bucket")
class TestGetTableNames:
    """testing get table names function"""

    @pytest.mark.it("table names retrieves list of table names")
    def test_table_names_gets_list_of_table_names(
        self, secretsmanager_client, table_names
    ):
        expected = table_names
        result = get_table_names()
        for table in expected:
            assert table in result

    @pytest.mark.it("table names logs error if database cannot be accessed")
    def test_logs_error_if_db_cannot_be_accessed(
        self, invalid_db_credentials, caplog, s3_client, table_names
    ):

        with caplog.at_level(logging.ERROR):
            get_table_names()
            assert "Tables names cannot be accessed" in caplog.text


class TestRetrieveDateTimeParameter:
    """test retrieve date time parameter function"""

    @pytest.mark.it("retrieves parameter from ssm parameter store")
    def test_retrieves_parameter_from_ssm_parameter_store(self, ssm_client):
        ssm_client.put_parameter(Name="latest-extract", Type="String", Value="test")
        assert retrieve_datetime_parameter() == "test"

    @pytest.mark.it("logs error if parameter not found")
    def test_logs_error_if_parameter_not_found(self, ssm_client, caplog):
        with caplog.at_level(logging.INFO):
            retrieve_datetime_parameter()
            assert "Could not retrieve date parameter:" in caplog.text


class TestSaveDateTimeParameter:
    """test dave date time paramenter function"""

    @pytest.mark.it("saves parameter to ssm parameter store")
    def test_saves_parameter_to_ssm_parameter_store(self, ssm_client):
        save_datetime_parameter("hello")
        assert retrieve_datetime_parameter() == "hello"


@patch("src.extract.BUCKET_NAME", "test-ingestion-bucket")
class TestListBucketObjects:
    @pytest.mark.it("returns 0 when no objects in bucket")
    def test_returns_0_for_empty_bucket(self, s3_client):
        assert list_bucket_objects() == 0

    @pytest.mark.it("returns number of objects when objects in bucket")
    def test_returns_1_for_1_item_in_bucket(self, s3_client):
        s3_client.put_object(
            Bucket="test-ingestion-bucket", Body="hello", Key="test.txt"
        )
        assert list_bucket_objects() == 1
