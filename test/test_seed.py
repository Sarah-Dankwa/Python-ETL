from db.connection import connect_to_db
from pg8000.native import identifier
import pytest
from test_seed_data import (
    warehouse_columns,
    oltp_columns,
    oltp_table_lengths,
    oltp_first_rows,
)
from db.seed import seed_warehouse, seed_oltp, get_oltp_tables, get_warehouse_tables


@pytest.fixture(scope="class")
def warehouse_db():
    """connects to local database & adds empty tables for the warehouse

    yields a connection to the local database
    then closes the connection
    """

    db = None
    try:
        db = connect_to_db()
        seed_warehouse(db)
        yield db
    finally:
        if db:
            db.close()


@pytest.fixture(scope="class")
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
def col_names_query():
    """base query to return column names for a given table"""

    query = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = :table"""
    return query


class TestOLTPSeedTables:
    """testing correct tables and columns added to database by OLTP seed"""

    @pytest.mark.it("test expected tables exist in OLTP database")
    def test_expected_tables_exist_in_OLTP_test_database(self, oltp_db):
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';"""
        expected = get_oltp_tables()
        result = oltp_db.run(query)
        for table in expected:
            assert [table] in result

    @pytest.mark.it("test OLTP tables have expected columns")
    @pytest.mark.parametrize("table_name,expected", oltp_columns)
    def test_expected_columns_in_oltp_database(
        self, oltp_db, col_names_query, table_name, expected
    ):
        """tests all tables in the oltp database have the expected columns

        parameterised using imported data from test_seed_data.py
        runs the same query for every tuple in the oltp_columns list
        """

        result = oltp_db.run(col_names_query, table=table_name)
        for column in expected:
            assert [column] in result


class TestOLTPSeedData:
    """testing the correct data was added to the oltp database"""

    @pytest.mark.it("test each table has the expected number of rows")
    @pytest.mark.parametrize("table_name,expected", oltp_table_lengths)
    def test_expected_table_length(
        self, oltp_db, col_names_query, table_name, expected
    ):
        """tests all tables in the oltp database have the expected number
        of rows

        parameterised using imported data from test_seed_data.py
        runs the same test for every tuple in the oltp_table_lengths list
        """
        query = f"SELECT * FROM {identifier(table_name)};"
        result = oltp_db.run(query)
        assert len(result) == expected

    @pytest.mark.it("test each table has the expected first row")
    @pytest.mark.parametrize("table_name,expected", oltp_first_rows)
    def test_expected_first_row(self, oltp_db, col_names_query, table_name, expected):
        """tests all tables in the oltp database have the expected values in
        the first row

        parameterised using imported data from test_seed_data.py
        runs the same test for every tuple in the oltp_first_rows list
        """
        query = f"SELECT * FROM {identifier(table_name)} LIMIT 1;"
        result = oltp_db.run(query)
        print(result[0])
        assert result[0] == expected


class TestWarehouseSeed:
    @pytest.mark.it("test expected tables exist in test warehouse")
    def test_expected_tables_exist_in_test_warehouse(self, warehouse_db):
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';"""

        expected = get_warehouse_tables()
        result = warehouse_db.run(query)
        for table in expected:
            assert [table] in result

    @pytest.mark.it("test tables have expected columns")
    @pytest.mark.parametrize("table_name,expected", warehouse_columns)
    def test_expected_columns(
        self, warehouse_db, col_names_query, table_name, expected
    ):
        """tests all tables in the warehouse have the expected columns

        parameterised using imported data from test_seed_data.py
        checks all tables have the expected columns
        """

        result = warehouse_db.run(col_names_query, table=table_name)
        for column in expected:
            assert [column] in result
