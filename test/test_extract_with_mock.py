import pytest
import boto3
from moto import mock_aws
import os
from unittest.mock import patch, call
from src.extract import (
    get_database_credentials,
    retrieve_datetime_parameter,
    save_datetime_parameter,
    list_bucket_objects,
    fetch_from_db,
    lambda_handler,
)


@pytest.fixture
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"


@pytest.fixture
def secretsmanager_client(aws_credentials):
    with mock_aws():
        yield boto3.client("secretsmanager", region_name="eu-west-2")


@pytest.fixture
def ssm_client(aws_credentials):
    with mock_aws():
        yield boto3.client("ssm", region_name="eu-west-2")


@pytest.fixture
def s3_client(aws_credentials):
    with mock_aws():
        client = boto3.client("s3")
        client.create_bucket(
            Bucket="test-bucket",
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
        )
        yield client


class TestDatabaseCredsAndConnection:
    @pytest.mark.it("get database credentials retrieves secret")
    def test_get_database_credentials(self, secretsmanager_client):
        secretsmanager_client.create_secret(
            Name="totesys-database", SecretString='{"key": "value2"}'
        )

        response = get_database_credentials()
        assert response == {"key": "value2"}


class TestRetrieveDateTimeParameter:
    @pytest.mark.it("retrieves parameter from ssm parameter store")
    def test_retrieves_parameter_from_ssm_parameter_store(self, ssm_client):
        ssm_client.put_parameter(Name="latest-extract", Type="String", Value="test")
        assert retrieve_datetime_parameter() == "test"


class TestSaveDateTimeParameter:
    @pytest.mark.it("saves parameter to ssm parameter store")
    def test_saves_parameter_to_ssm_parameter_store(self, ssm_client):
        save_datetime_parameter("hello")
        assert retrieve_datetime_parameter() == "hello"


class TestListBucketObjects:
    @pytest.mark.it("returns 0 when no objects in bucket")
    @patch("src.extract.BUCKET_NAME", "test-bucket")
    def test_returns_0_for_empty_bucket(self, s3_client):
        assert list_bucket_objects() == 0

    @pytest.mark.it("returns number of objects when objects in bucket")
    @patch("src.extract.BUCKET_NAME", "test-bucket")
    def test_returns_1_for_1_item_in_bucket(self, s3_client):
        s3_client.put_object(Bucket="test-bucket", Body="hello", Key="test.txt")
        assert list_bucket_objects() == 1


class TestFullFetch:
    @pytest.mark.it("fetch from db calls get_table_names function")
    @patch("src.extract.BUCKET_NAME", "test-bucket")
    @patch("src.extract.get_table_names", return_value=["a", "b", "c"])
    @patch("src.extract.get_single_table", return_value={})
    def test_full_fetch_calls_get_table_names(
        self, mock_single_table, mock_table_names, s3_client
    ):
        fetch_from_db()
        mock_table_names.assert_called()

    @pytest.mark.it("fetch from db calls get_single_table with expected arguments")
    @patch("src.extract.BUCKET_NAME", "test-bucket")
    @patch("src.extract.get_table_names", return_value=["a", "b", "c"])
    @patch("src.extract.get_single_table", return_value={})
    def test_full_fetch_calls_get_single_table(
        self, mock_single_table, mock_table_names, s3_client
    ):
        expected_calls = [call("a", None), call("b", None), call("c", None)]
        fetch_from_db()
        assert mock_single_table.mock_calls == expected_calls

    @pytest.mark.it("fetch from db adds objects to s3 bucket with expected keys")
    @patch("src.extract.BUCKET_NAME", "test-bucket")
    @patch("src.extract.year", "2020")
    @patch("src.extract.month", "10")
    @patch("src.extract.day", "10")
    @patch("src.extract.time", "13:40")
    @patch("src.extract.get_table_names", return_value=["a", "b", "c"])
    @patch("src.extract.get_single_table", return_value=[{"test": "test"}])
    def test_full_fetch_uploads_files_to_s3(
        self, mock_single_table, mock_table_names, s3_client
    ):
        expected_keys = [
            "a/2020/10/10/13:40/a.parquet",
            "b/2020/10/10/13:40/b.parquet",
            "c/2020/10/10/13:40/c.parquet",
        ]
        fetch_from_db()
        objects = s3_client.list_objects_v2(Bucket="test-bucket")
        returned_keys = [o["Key"] for o in objects["Contents"]]
        assert returned_keys == expected_keys


class TestLambdaHandler:
    @pytest.mark.it("lambda_handler calls list objects function")
    @patch("src.extract.save_datetime_parameter")
    @patch("src.extract.fetch_from_db")
    @patch("src.extract.list_bucket_objects", return_value=0)
    def test_lambda_handler_calls_list_objects_function(
        self, mock_list_objects, mock_fetch_from_db, mock_save_parameter, s3_client
    ):
        lambda_handler()
        mock_list_objects.assert_called()

    @pytest.mark.it("when bucket is not empty retrieve datetime parameter is called")
    @patch("src.extract.retrieve_datetime_parameter")
    @patch("src.extract.save_datetime_parameter")
    @patch("src.extract.fetch_from_db")
    @patch("src.extract.list_bucket_objects", return_value=1)
    def test_lambda_handler_calls_retrieve_date_time_param(
        self,
        mock_list_objects,
        mock_fetch_from_db,
        mock_save_parameter,
        mock_date_time,
        s3_client,
    ):
        lambda_handler()
        mock_date_time.assert_called()

    @pytest.mark.it(
        "when bucket is empty lambda handler calls full " + "fetch with no arguments"
    )
    @patch("src.extract.save_datetime_parameter")
    @patch("src.extract.fetch_from_db")
    @patch("src.extract.list_bucket_objects", return_value=0)
    def test_lambda_handler_calls_full_fetch_with_no_args(
        self, mock_list_objects, mock_fetch_from_db, mock_save_parameter, s3_client
    ):
        lambda_handler()
        mock_fetch_from_db.assert_called_with()

    @pytest.mark.it(
        "when bucket is not empty lambda handler calls"
        + " fetch from db expected argument"
    )
    @patch("src.extract.retrieve_datetime_parameter", return_value="expected")
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
    ):
        lambda_handler()
        mock_fetch_from_db.assert_called_with("expected")

    @pytest.mark.it("lambda handler calls save date time parameter")
    @patch("src.extract.save_datetime_parameter")
    @patch("src.extract.fetch_from_db")
    @patch("src.extract.list_bucket_objects", return_value=0)
    def test_lambda_handler_calls_save_datetime_parameter(
        self, mock_list_objects, mock_fetch_from_db, mock_save_parameter, s3_client
    ):
        lambda_handler()
        mock_save_parameter.assert_called()
