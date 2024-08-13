import pytest
import boto3
from moto import mock_aws
import os
from src.extract import get_database_credentials


@pytest.fixture(scope="function")
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"


@pytest.fixture(scope="function")
def secretsmanager_client(aws_credentials):
    with mock_aws():
        yield boto3.client("secretsmanager", region_name="eu-west-2")


class TestDatabaseCredsAndConnection:
    @pytest.mark.it("get database credentials retrieves secret")
    def test_get_database_credentials(self, secretsmanager_client):
        secretsmanager_client.create_secret(
            Name="totesys-database", SecretString='{"key": "value2"}'
        )

        response = get_database_credentials()
        assert response == {"key": "value2"}
