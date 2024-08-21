from src.transform import (dim_date, read_parquet_from_s3, write_parquet_to_s3_bucket, 
fact_sales_order, dim_design, dim_currency, get_all_files, dim_staff, dim_counterparty,
 dim_location, lambda_handler)
import pytest
from datetime import datetime
from unittest.mock import patch, call, Mock
import logging
import json
import pyarrow.parquet as pq
import pandas as pd
import boto3
from moto import mock_aws
import os



FAKE_TIME_STR = "2024-08-20T02:02:02"

@pytest.fixture
def patch_datetime_now():
    with patch("datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value.isoformat.return_value = FAKE_TIME_STR
        yield mock_datetime


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"

@pytest.fixture(scope="function")
def s3(aws_credentials):
    """
    Return a mocked S3 client
    """
    with mock_aws():
        yield boto3.client("s3", region_name="eu-west-2")

@pytest.fixture(scope="function")
def mocked_aws(aws_credentials):
    """
    Mock all AWS interactions
    Requires you to create your own boto3 clients
    """
    with mock_aws():
        yield

@pytest.fixture
def create_bucket1(s3):
    s3.create_bucket(Bucket="test_bucket")


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


@patch("src.transform.INGEST_BUCKET_NAME", "nc-alapin-extract-test-bucket")
class TestRemodellingcurrency():
    @pytest.mark.it("Testing remodelling currency dimension table")
    def test_remodelling_dim_currency_table(self):
        keys = ['currency/2024/08/19/23:17:17/currency.parquet']
        df = read_parquet_from_s3(keys)
        currency_df = dim_currency(df)
        assert ["currency_id", "currency_code", "currency_name"] == list(currency_df.columns) 
        assert currency_df["currency_name"][0] == "British pound"
        assert currency_df["currency_name"][1] == "United States dollar"
        assert currency_df["currency_name"][2] == "European Euro"

    @pytest.mark.it("Testing remodelling currency dimension table handles error")
    def test_remodelling_dim_currency_table_error_handling(self, caplog):
        df1 = pd.DataFrame()
        
        with caplog.at_level(logging.ERROR):
            currency_df = dim_currency(df1)
            assert "failed to create dim_currency dataframe" in caplog.text 


@patch("src.transform.INGEST_BUCKET_NAME", "nc-alapin-extract-test-bucket")
class TestGetAllFiles():
    @pytest.mark.it("Testing Get All Files function from S3 table prefix")
    def test_get_all_files(self):
        prefix_1 = "sales_order"
        list_files_1 = get_all_files(prefix_1)
        prefix_2 = "department"
        list_files_2 = get_all_files(prefix_2)
        assert ['sales_order/2024/08/19/23:17:17/sales_order.parquet',
                'sales_order/2024/08/20/23:17:18/23:17:17/sales_order.parquet'] == list_files_1
        assert ['department/2024/08/19/23:17:17/department.parquet'] == list_files_2
        

    @pytest.mark.it("Testing get all files handles error")
    def test_get_all_files_error_handling(self, caplog):
       
        with caplog.at_level(logging.ERROR):
            prefix_2 = "dpartment"
            list_files_2 = get_all_files(prefix_2)
            assert "failed to load files" in caplog.text 


@patch("src.transform.INGEST_BUCKET_NAME", "nc-alapin-extract-test-bucket")
class TestRemodellingStaff():
    @pytest.mark.it("Testing remodelling staff dimension table")
    def test_remodelling_dim_staff_table(self):
        keys = ['staff/2024/08/19/23:17:17/staff.parquet']
        df = read_parquet_from_s3(keys)
        staff_df = dim_staff(df)
        assert ["staff_id", "first_name", "last_name", "department_name", 
                                 "location","email_address"] == list(staff_df.columns)
        assert staff_df.shape == (20,6) 
        assert staff_df["first_name"][0] == "Jeremie"
        assert staff_df["location"][0] == "Manchester"
        assert staff_df["department_name"][0] == "Purchasing"

    @pytest.mark.it("Testing dim_staff handles error")
    def test_dim_staff_error_handling(self, caplog):
       
        with caplog.at_level(logging.ERROR):
            df1 = pd.DataFrame()
            staff_df = dim_staff(df1)
            assert "failed to create dim_staff dataframe" in caplog.text 

@patch("src.transform.INGEST_BUCKET_NAME", "nc-alapin-extract-test-bucket")
class TestRemodellingCounterparty():
    @pytest.mark.it("Testing remodelling counterparty dimension table")
    def test_remodelling_dim_counterparty_table(self):
        keys = ['counterparty/2024/08/19/23:17:17/counterparty.parquet']
        df = read_parquet_from_s3(keys)
        counterparty_df = dim_counterparty(df)
        assert ["counterparty_id", "counterparty_legal_name", "counterparty_legal_address_line_1", 
                "counterparty_legal_address_line_2", "counterparty_legal_district", "counterparty_legal_city",
                  "counterparty_legal_postal_code", "counterparty_legal_country", 
                  "counterparty_legal_phone_number"] == list(counterparty_df.columns) 
        assert counterparty_df.shape == (20,9)
        assert counterparty_df["counterparty_legal_name"][0] == "Fahey and Sons" 
        assert counterparty_df["counterparty_legal_address_line_1"][0] == "605 Haskell Trafficway" 
        assert counterparty_df["counterparty_legal_address_line_2"][0] == "Axel Freeway" 
        assert counterparty_df["counterparty_legal_district"][0] == None 
        assert counterparty_df["counterparty_legal_city"][0] == "East Bobbie" 
        assert counterparty_df["counterparty_legal_postal_code"][0] == "88253-4257" 
        assert counterparty_df["counterparty_legal_country"][0] == "Heard Island and McDonald Islands" 
        assert counterparty_df["counterparty_legal_phone_number"][0] == "9687 937447" 

    @pytest.mark.it("Testing dim_counterparty handles error")
    def test_dim_counterparty_error_handling(self, caplog):
       
        with caplog.at_level(logging.ERROR):
            df1 = pd.DataFrame()
            staff_df = dim_counterparty(df1)
            assert "failed to create dim_counterparty dataframe" in caplog.text 


@patch("src.transform.INGEST_BUCKET_NAME", "nc-alapin-extract-test-bucket")
class TestRemodellingLocation():
    @pytest.mark.it("Testing remodelling Location dimension table")
    def test_remodelling_dim_location_table(self):
        keys = ['address/2024/08/19/23:17:17/address.parquet']
        df = read_parquet_from_s3(keys)
        location_df = dim_location(df)
        assert ["location_id", "address_line_1", "address_line_2", "district", 
                                    "city", "postal_code", "country", "phone"]== list(location_df.columns) 
        assert location_df.shape == (30,8)
        assert location_df["location_id"][0] == 1 
        assert location_df["address_line_1"][0] == "6826 Herzog Via" 
        assert location_df["address_line_2"][0] == None 
        assert location_df["district"][0] == "Avon" 
        assert location_df["city"][0] == "New Patienceburgh" 
        assert location_df["postal_code"][0] == "28441" 
        assert location_df["country"][0] == "Turkey" 
        assert location_df["phone"][0] == "1803 637401"

    @pytest.mark.it("Testing dim_location handles error")
    def test_dim_location_error_handling(self, caplog):
       
        with caplog.at_level(logging.ERROR):
            df1 = pd.DataFrame()
            location_df = dim_location(df1)
            assert "failed to create dim_location dataframe" in caplog.text 


@patch("src.transform.INGEST_BUCKET_NAME", "nc-alapin-extract-test-bucket")
class TestLambdaHandler():
    @pytest.mark.skip("Testing Lambda Handler table")
    @patch("src.transform.year", "2024")
    @patch("src.transform.month", "08")
    @patch("src.transform.day", "21")
    @patch("src.transform.time", "01:01:01")
    def test_lambda_handler_full_load(self, create_bucket1):        
        file_path_list = lambda_handler()
        assert file_path_list == ['fact_sales_order/2024/08/21/01:01:01/fact_sales_order.parquet', 
                'dim_location/2024/08/21/01:01:01/dim_location.parquet',
                'dim_counterparty/2024/08/21/01:01:01/dim_counterparty.parquet',
                'dim_staff/2024/08/21/01:01:01/dim_staff.parquet',
                'dim_currency/2024/08/21/01:01:01/dim_currency.parquet',
                'dim_design/2024/08/21/01:01:01/dim_design.parquet',
                'dim_date/2024/08/21/01:01:01/dim_date.parquet']



    @pytest.mark.it("Testing Lambda handler to write event/key files to S3 bucket")
    @patch("src.transform.TRANSFORM_BUCKET_NAME", "nc-alapin-transfrom-test-bucket")
    @patch("src.transform.year", "2024")
    @patch("src.transform.month", "08")
    @patch("src.transform.day", "21")
    @patch("src.transform.time", "01:01:01")
    def test_writing_files_to_s3(self):
        keys = ['sales_order/2024/08/20/23:17:18/23:17:17/sales_order.parquet', 
                'staff/2024/08/19/23:17:17/staff.parquet',
                'department/2024/08/19/23:17:17/department.parquet', 
                'counterparty/2024/08/19/23:17:17/counterparty.parquet']
        file_list = lambda_handler(event=keys)       
        assert file_list == ['fact_sales_order/2024/08/21/01:01:01/fact_sales_order.parquet', 
                'dim_staff/2024/08/21/01:01:01/dim_staff.parquet',
                'dim_counterparty/2024/08/21/01:01:01/dim_counterparty.parquet']
        

    @pytest.mark.it("Testing Lambda handler to write empty event file list to S3 bucket")
    @patch("src.transform.TRANSFORM_BUCKET_NAME", "nc-alapin-transfrom-test-bucket")
    def test_writing_empty_list_to_s3(self, caplog):
        keys = []
        
        with caplog.at_level(logging.INFO):
            file_list = lambda_handler(event=keys)       
            assert file_list == []
            assert "No new files to transfrom" in caplog.text
            

    @pytest.mark.it("Testing Lambda handler for error handling with wrong S3 bucket")
    @patch("src.transform.TRANSFORM_BUCKET_NAME", "")
    def test_error_handling_invalid_bucket(self, caplog):
        keys = ['sales_order/2024/08/20/23:17:18/23:17:17/sales_order.parquet', 
                'staff/2024/08/19/23:17:17/staff.parquet',
                'department/2024/08/19/23:17:17/department.parquet']
        with caplog.at_level(logging.ERROR):
            file_list = lambda_handler(event=keys)       
            assert "Transform lambda failed to complete" in caplog.text
    

    