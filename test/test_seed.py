"""tests run using a test database using database credentials from .env file
must add following environment variables to .env file:
    LOCAL_USER=
    LOCAL_PASSWORD=
    LOCAL_DATABASE=test_warehouse
    LOCAL_HOST=localhost
    LOCAL_PORT=5432
and run following command:
    >>> psql -f db/db.sql
before running tests
"""

from db.seed import seed_warehouse
from db.connection import connect_to_db
import pytest
from test_seed_data import testdata

@pytest.fixture
def conn():
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
def col_names_query():
    """base query to return column names for a given table"""
    
    query = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = :table"""
    return query


@pytest.mark.it('test expected tables exist in database')
def test_expected_tables_exist_in_test_database(conn):
    query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public';"""
    expected = [
        'fact_sales_order', 
        'dim_staff', 
        'dim_location', 
        'dim_design',
        'dim_date',
        'dim_currency',
        'dim_counterparty',
    ]

    result = conn.run(query)
    for table in expected:
        assert [table] in result


@pytest.mark.it('test tables have expected columns')
@pytest.mark.parametrize("table_name,expected", testdata)
def test_expected_columns(conn, col_names_query, table_name, expected):
    """tests all tables in the warehouse have the expected columns
    
    parameterised using imported data from test_seed_data.py
    checks all tables have the expected columns
    """

    result = conn.run(col_names_query, table=table_name)
    for column in expected:
        assert [column] in result