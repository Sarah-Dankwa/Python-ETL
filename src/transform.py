from botocore.exceptions import ClientError
import boto3
import json
import pandas as pd
import os
from datetime import datetime
import logging
import pytz
import io

uk_time = pytz.timezone("Europe/London")
now = datetime.now(uk_time)
year = now.strftime("%Y")
month = now.strftime("%m")
day = now.strftime("%d")
time = now.strftime("%H:%M:%S")

logger = logging.getLogger()


logging.getLogger().setLevel(logging.INFO)
INGEST_BUCKET_NAME = os.environ.get("DATA_INGESTED_BUCKET_NAME")
TRANSFORM_BUCKET_NAME = os.environ.get("DATA_PROCESSED_BUCKET_NAME")

def read_parquet_from_s3(keys, s3_client=None):
    try:
        if s3_client is None:
            s3_client = boto3.client("s3")
        dfs = []
        for key in keys:
            obj = s3_client.get_object(Bucket=INGEST_BUCKET_NAME, Key=key)
            dfs.append(pd.read_parquet(io.BytesIO(obj['Body'].read())))
                
        final = pd.concat(dfs, ignore_index=True)
        return final
        
    except Exception as e:
         logger.error(f"Error{e} Key not found in S3")

def write_parquet_to_s3_bucket(df, prefix, s3_client=None):
    try: 
        if s3_client is None:
            s3_client = boto3.client("s3")     
        bucket_name = TRANSFORM_BUCKET_NAME
        filename = f"/tmp/{prefix}.parquet"
        key = (
            prefix
            + "/"
            + year
            + "/"
            + month
            + "/"
            + day
            + "/"
            + time
            + "/"
            + prefix
            + ".parquet"
        )
        df.to_parquet(filename, index=False)
        s3_client.upload_file(filename, bucket_name, key)
        logger.info(f"{filename} files added to s3 bucket")
        return key
    except Exception as e:
         logger.error(f"Error{e} File failed to upload")

def dim_date(start='2021-01-01', end='2024-09-30'):
     try:         
        df = pd.DataFrame({"date_id": pd.date_range(start, end)})
        df["day_name"] = df.date_id.dt.strftime('%A')
        df["day"] = df.date_id.dt.day
        df["day_of_week"] = df.date_id.dt.day_of_week
        df["month"] = df.date_id.dt.month
        df["month_name"] = df.date_id.dt.strftime('%B')
        df["quarter"] = df.date_id.dt.quarter
        df["year"] = df.date_id.dt.year
        df["date_id"] = df["date_id"].dt.strftime("%Y-%m-%d")
        return df
     except Exception as e:
         logger.error(f"Error{e} while creating a date dimension table")

#dim_date()

def fact_sales_order(sales_order_df):
    try:
        fact_sales_order_df = pd.DataFrame()
        fact_sales_order_df = sales_order_df[["sales_order_id", "created_at", "last_updated",  "staff_id", "counterparty_id", "units_sold", 
                                              "unit_price", "currency_id", "design_id", "agreed_delivery_date", "agreed_payment_date", 
                                              "agreed_delivery_location_id"]]
        print(fact_sales_order_df.shape)
        fact_sales_order_df['created_date'] = fact_sales_order_df['created_at'].dt.date
        fact_sales_order_df['created_time'] = fact_sales_order_df['created_at'].dt.time
        fact_sales_order_df['last_updated_date'] = fact_sales_order_df['last_updated'].dt.date
        fact_sales_order_df['last_updated_time'] = fact_sales_order_df['last_updated'].dt.time
        df = fact_sales_order_df.drop(["created_at","last_updated"], axis=1)  
        df.rename(columns={"staff_id": "sales_staff_id"}, inplace = True)
        print(df.shape)
        return df
    except Exception as e:
        logger.error(f"Error{e} failed to create fact_sales_order dataframe")


def dim_design(design_df):
    try:
        dim_design_df = pd.DataFrame()
        dim_design_df = design_df[["design_id", "design_name", "file_location",  "file_name"]]

        return dim_design_df
    except Exception as e:
        logger.error(f"Error{e} failed to create dim_design dataframe")



def lambda_handler(event, context):
    return {"statusCode": 200, "body": "Hello test lambda!"}

''' 
1. Extratc Lambda outputs the list of files added to the extract s3 bucket
2. Based on the list of parquete files from Extract Lambda, Read the parquete from extract S3 bucket one by one
3. Merge all the parqetes and create one single dataframe(Master) (for now specific fact_sales_order schema)
4. Create fact_sales_order dataframe using Master dataframe 
5. Create dim_staff dataframe by using Master dataframe 
6. Create fact_sales_order dataframe by using Master dataframe 
'''

'''
postgres Fact and Dimention table dependancy tables from the Totesys database
dim_counterparty -> counterparty and address
dim_date -> standalone
dim_staff -> staff and department
dim_location -> address and sales_order
dim_currency -> currency
dim_design -> design
fact_sales_order -> sales_order, dim_design, dim_currency, dim_location, dim_staff, dim_date and dim_counterparty
'''