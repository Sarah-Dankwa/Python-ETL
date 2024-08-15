import pytest
from unittest.mock import patch
from pg8000.native import Connection
from db.seed import seed
from db.connection import db
from src.load import (
    get_warehouse_credentials,
    get_latest_data_for_one_table,
    db_connection,
    insert_new_data_into_data_warehouse,
    lambda_handler
)


@pytest.fixture(scope="module")
def run_seed():
    '''Runs seed before starting tests, yields, runs tests,
       then closes connection to db'''
    seed()
    yield
    db.close()


class TestGetWarehouseCredentials:
    '''tests for the get warehouse credentials function'''
    @pytest.mark.skip('credentials not yet known')
    @pytest.mark.it('function can access secret from secrets manager')
    def test_function_accesses_secret(self, secretsmanager_client):
        pass
    


class TestGetLatestDataForOneTable:
    '''tests for the get latest data for one table function'''
    @pytest.mark.skip('need a test parquet file to ')
    @pytest.mark.it('function returns a list of dictionaries')
    def test_function_returns_a_list_of_dictionaries(self, s3_client):
        pass


class TestDBConnection:
    '''tests for the db connection function'''
    
    @pytest.mark.skip
    @pytest.mark.it("Test db connection connects to database")
    def test_connection_to_db(self):
        db = db_connection()
        assert isinstance(db, Connection)


class TestInsertNewDataIntoWarehouse:
    '''tests for insert new data into warehouse function'''
    @pytest.mark.skip
    @pytest.mark.it('inserts data into warehouse')
    def test_data_is_inserted_into_warehouse(self):
        pass


class TestLambdaHandler:
    '''tests for the lambda handler'''
    pass
