from db.seed import seed_warehouse, seed_oltp, get_oltp_tables, get_warehouse_tables
from db.connection import connect_to_db
import pytest
from test_seed_data import warehouse_testdata, oltp_testdata

@pytest.fixture
def warehouse_conn():
    """seeds database and yields connection"""
    
    db = None
    try:
        db = connect_to_db()
        seed_warehouse(db)
        yield db
    finally:
        if db:
            db.close()


@pytest.fixture
def oltp_conn():
    """connects to local database & adds empty tables
    
    yields a connection to the local database 
    then closes the connection after each test is complete
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
def col_names_query():
    """base query to return column names for a given table"""
    
    query = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = :table"""
    return query


class TestOLTPSeed:
    @pytest.mark.it('test expected tables exist in OLTP database')
    def test_expected_tables_exist_in_OLTP_test_database(self, oltp_conn):
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';"""
        expected = get_oltp_tables()
        result = oltp_conn.run(query)
        for table in expected:
            assert [table] in result


    @pytest.mark.it('test OLTP tables have expected columns')
    @pytest.mark.parametrize("table_name,expected", oltp_testdata)
    def test_expected_columns_in_oltp_database(self, oltp_conn, col_names_query, table_name, expected):
        """tests all tables in the warehouse have the expected columns
        
        parameterised using imported data from test_seed_data.py
        checks all tables have the expected columns
        """

        result = oltp_conn.run(col_names_query, table=table_name)
        for column in expected:
            assert [column] in result

class TestWarehouseSeed:
    @pytest.mark.it('test expected tables exist in test warehouse')
    def test_expected_tables_exist_in_test_warehouse(self, warehouse_conn):
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';"""
        
        expected = get_warehouse_tables()
        result = warehouse_conn.run(query)
        for table in expected:
            assert [table] in result


    @pytest.mark.it('test tables have expected columns')
    @pytest.mark.parametrize("table_name,expected", warehouse_testdata)
    def test_expected_columns(self, warehouse_conn, col_names_query, table_name, expected):
        """tests all tables in the warehouse have the expected columns
        
        parameterised using imported data from test_seed_data.py
        checks all tables have the expected columns
        """

        result = warehouse_conn.run(col_names_query, table=table_name)
        for column in expected:
            assert [column] in result
