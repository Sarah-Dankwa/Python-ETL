import pytest
from pg8000.native import Connection
from src.extract import (
    connect_to_db,
    get_single_table,
    get_table_names,
    get_last_updated
)


class TestDatabaseCredsAndConnection:
    @pytest.mark.it("Test db connection connects to database")
    def test_connection_to_db(self):
        db = connect_to_db()
        assert isinstance(db, Connection)


class TestGetSingleTable:
    @pytest.mark.it("Test returns correct keys for payment type table")
    def test_returns_expected_keys(self):
        results = get_single_table("payment_type")
        assert "payment_type_id" in results[0]
        assert "payment_type_name" in results[0]
        assert "created_at" in results[0]
        assert "last_updated" in results[0]


class TestGetTableNames:
    def test_table_names_gets_list_of_table_names(self):
        expected = [
            'address',
            'staff', 
            'payment',
            'department', 
            'transaction',
            'currency', 
            'payment_type',
            'sales_order', 
            'counterparty',
            'purchase_order',
            'design'
        ]
        assert get_table_names() == expected


class TestGetLastUpdated:
    pass

class TestFullFetch:
    pass
