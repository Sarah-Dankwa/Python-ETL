import pytest
from pg8000.native import Connection
from datetime import datetime
import pyarrow.parquet as pq
from src.extract import (
    connect_to_db,
    convert_to_parquet,
    get_single_table,
    get_table_names,
)


class TestDatabaseCredsAndConnection:
    @pytest.mark.it("Test db connection connects to database")
    def test_connection_to_db(self):
        db = connect_to_db()
        assert isinstance(db, Connection)


class TestGetSingleTable:
    @pytest.mark.it("Test returns a list of dictionaries")
    def test_returns_list_of_dictionaries(self):
        results = get_single_table("payment_type")
        assert isinstance(results, list)
        for item in results:
            assert isinstance(item, dict)

    @pytest.mark.it("Test returns correct keys for payment type table")
    def test_returns_expected_keys(self):
        results = get_single_table("payment_type")
        assert "payment_type_id" in results[0]
        assert "payment_type_name" in results[0]
        assert "created_at" in results[0]
        assert "last_updated" in results[0]

    @pytest.mark.it("when given date only returns entries after given date")
    def test_filters_table_by_given_date(self):
        sample_date = datetime(2022, 10, 20)
        results = get_single_table("sales_order", sample_date)
        for row in results:
            assert row["last_updated"] > sample_date


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


class TestGetTableNames:
    @pytest.mark.it("table names retrieves list of table names")
    def test_table_names_gets_list_of_table_names(self):
        expected = [
            "address",
            "staff",
            "payment",
            "department",
            "transaction",
            "currency",
            "payment_type",
            "sales_order",
            "counterparty",
            "purchase_order",
            "design",
        ]
        assert get_table_names() == expected
