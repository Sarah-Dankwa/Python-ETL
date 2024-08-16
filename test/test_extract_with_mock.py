import pytest
from unittest.mock import patch, call
from dotenv import load_dotenv
from datetime import datetime
from src.extract import (
    fetch_from_db,
    lambda_handler,
)

@pytest.fixture(autouse=True)
def extract_fixtures(
    #patch_bucket_name,
    secretsmanager_client,
    s3_client,
    ssm_client
):
    yield


















