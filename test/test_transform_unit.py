from src.transform import dim_date, read_parquet_from_s3, write_parquet_to_s3_bucket, fact_sales_order, dim_design
import pytest
from datetime import datetime
from unittest.mock import patch, call, Mock
import logging
import json
import pyarrow.parquet as pq
import pandas as pd
import boto3



FAKE_TIME_STR = "2024-08-20T02:02:02"

@pytest.fixture
def patch_datetime_now():
    with patch("datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value.isoformat.return_value = FAKE_TIME_STR
        yield mock_datetime


class TestDimentionDate:
    """tests for get dimention date function"""

    @pytest.mark.it("Dimention date function has all the columns")
    def test_dim_date_has_all_columns(self):
        #arrange
        #act
        df = dim_date()
        #assert
        assert ['date_id', 'day_name', 'day', 'day_of_week', 'month', 'month_name','quarter','year'] == list(df.columns)

    @pytest.mark.it("Dimention date function return correct date range")
    def test_dim_date_return_date_range(self):
        #arrange
        #act
        df = dim_date('08-01-2024', '08-30-2024')
        #assert
        assert df['date_id'].iloc[0] ==  '2024-08-01'
        assert df['date_id'].iloc[-1] ==  '2024-08-30'
        assert df['day_name'].iloc[0] ==  'Thursday'
        assert df['day_name'].iloc[-1] ==  'Friday'
        assert df['day'].iloc[0] ==  1
        assert df['day'].iloc[-1] ==  30
        assert df['day_of_week'].iloc[0] ==  3
        assert df['day_of_week'].iloc[-1] ==  4
        assert df['month'].iloc[0] ==  8
        assert df['month'].iloc[-1] ==  8
        assert df['month_name'].iloc[0] ==  'August'
        assert df['month_name'].iloc[-1] ==  'August'
        assert df['quarter'].iloc[0] ==  3
        assert df['quarter'].iloc[-1] ==  3
        assert df['year'].iloc[0] ==  2024
        assert df['year'].iloc[-1] ==  2024
        assert len(df.index) ==  30


@patch("src.transform.INGEST_BUCKET_NAME", "nc-alapin-extract-test-bucket")
class TestReadParquteFromS3():
    @pytest.mark.it("Testing read_parquet_from_s3 reading file from S3 bucket")
    def test_reading_single_file_from_s3(self):
        keys = ['sales_order/2024/08/19/23:17:17/sales_order.parquet']
        df = read_parquet_from_s3(keys)
        assert df.shape == (9798,12)
        assert type(df) == pd.DataFrame

    @pytest.mark.it("Testing read_parquet_from_s3 raising error file from S3 bucket is not available")
    def test_reading_unavailable_file_from_s3(self, caplog):
        keys = 'sales_order/2024/08/19/23:17:17/sales.parquet'
        with caplog.at_level(logging.ERROR):
            read_parquet_from_s3(keys)
            assert "Key not found" in caplog.text

    @pytest.mark.it("Testing read_parquet_from_s3 reading multiple files from S3 bucket")
    def test_reading_multiple_files_from_s3(self):
        keys = ['sales_order/2024/08/19/23:17:17/sales_order.parquet', 'sales_order/2024/08/20/23:17:18/23:17:17/sales_order.parquet']
        df = read_parquet_from_s3(keys)
        assert df.shape == (19596,12)
        assert type(df) == pd.DataFrame


@patch("src.transform.INGEST_BUCKET_NAME", "nc-alapin-extract-test-bucket")
class TestWriteParquteToS3():
    @pytest.mark.it("Testing write_parquet_to_s3_bucket writing single parqet file to S3 bucket")
    @patch("src.transform.TRANSFORM_BUCKET_NAME", "nc-alapin-transfrom-test-bucket")
    @patch("src.transform.year", "2024")
    @patch("src.transform.month", "08")
    @patch("src.transform.day", "20")
    @patch("src.transform.time", "05:05:05")
    def test_writing_single_file_to_s3(self):
        keys = ['sales_order/2024/08/19/23:17:17/sales_order.parquet']
        df = read_parquet_from_s3(keys)
        key = write_parquet_to_s3_bucket(df, 'sales_order')
        assert key == 'sales_order/2024/08/20/05:05:05/sales_order.parquet'
        s3 = boto3.resource('s3')
        bucket = s3.Bucket("nc-alapin-transfrom-test-bucket")
        bucket.objects.all().delete()


    @pytest.mark.it("Testing write_parquet_to_s3_bucket writing parqet file to not existing S3 bucket")
    @patch("src.transform.TRANSFORM_BUCKET_NAME", "")
    @patch("src.transform.year", "2024")
    @patch("src.transform.month", "08")
    @patch("src.transform.day", "20")
    @patch("src.transform.time", "06:06:06")
    def test_writing_single_file_to_s3(self, caplog):
        keys = ['sales_order/2024/08/19/23:17:17/sales_order.parquet']
        df = read_parquet_from_s3(keys)
        with caplog.at_level(logging.ERROR):
            key = write_parquet_to_s3_bucket(df, 'sales_order')
            assert "File failed to upload" in caplog.text
        

@patch("src.transform.INGEST_BUCKET_NAME", "nc-alapin-extract-test-bucket")
class TestRemodellingSalesOrder():
    @pytest.mark.it("Testing remodelling sales order fact table")
    def test_remodelling_sales_order_fact_table(self):
        keys = ['sales_order/2024/08/19/23:17:17/sales_order.parquet']
        df = read_parquet_from_s3(keys)
        fact_sales_order_df = fact_sales_order(df)
        #assert type(fact_sales_order_df) == pd.DataFrame
        assert ["sales_order_id" ,"sales_staff_id" ,
        "counterparty_id" ,"units_sold" ,"unit_price" ,"currency_id" ,"design_id"  ,
        "agreed_delivery_date","agreed_payment_date","agreed_delivery_location_id" ,
        "created_date" ,"created_time" ,"last_updated_date" ,"last_updated_time" ] == list(fact_sales_order_df.columns) 
        

    @pytest.mark.it("Testing remodelling sales order fact table handles error")
    def test_remodelling_sales_order_fact_table_error_handling(self, caplog):
        df1 = pd.DataFrame()
        
        with caplog.at_level(logging.ERROR):
            fact_sales_order_df = fact_sales_order(df1)
            assert "failed to create fact_sales_order dataframe" in caplog.text 


@patch("src.transform.INGEST_BUCKET_NAME", "nc-alapin-extract-test-bucket")
class TestRemodellingdesign():
    @pytest.mark.it("Testing remodelling design dimension table")
    def test_remodelling_dim_design_table(self):
        keys = ['design/2024/08/19/23:17:17/design.parquet']
        df = read_parquet_from_s3(keys)
        design_df = dim_design(df)
        assert ["design_id", "design_name", "file_location",  "file_name"] == list(design_df.columns) 
        

    @pytest.mark.it("Testing remodelling design dimension table handles error")
    def test_remodelling_dim_design_table_error_handling(self, caplog):
        df1 = pd.DataFrame()
        
        with caplog.at_level(logging.ERROR):
            design_df = dim_design(df1)
            assert "failed to create dim_design dataframe" in caplog.text 