from pg8000.native import Connection, identifier, literal
from botocore.exceptions import ClientError
import boto3
import json
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import os
from datetime import datetime
import logging 

logger = logging.getLogger() 

# logging.getLogger().setLevel(logging.INFO)


# delete line 14 and use this code to allow logger to work locally
if len(logging.getLogger().handlers) > 0:
    # The Lambda environment pre-configures a handler logging to stderr. If a handler is already configured,
    # `.basicConfig` does not execute. Thus we set the level directly.
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.basicConfig(level=logging.INFO)


# BUCKET_NAME = os.environ['BUCKET_NAME']
BUCKET_NAME = 'sarah-jessica-test-bucket'
now = datetime.now()
year = now.strftime('%Y')
month = now.strftime('%m')
day = now.strftime('%d')
time = now.strftime('%H:%M:%S')


def get_database_credentials():
    secret_name = "totesys-database"
    client = boto3.client("secretsmanager")

    try:
        get_secret_value = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e

    secret = get_secret_value["SecretString"]
    secret_dict = json.loads(secret)
    return secret_dict


def connect_to_db():
    secret = get_database_credentials()

    return Connection(
        user=secret["Username"],
        database=secret["Database"],
        password=secret["Password"],
        host=secret["Hostname"],
        port=secret["Port"]
    )


def get_single_table(table_name, fetch_date=None):
    db = connect_to_db()
    query = f"SELECT * FROM {identifier(table_name)}"

    if fetch_date:
        query += f" WHERE last_updated between {literal(fetch_date)} and {literal(str(now))};"
        # may have to determine difference between using idientifer or literal for fetch data &/or now variables
    
    
    results = db.run(query)
    columns = [col["name"] for col in db.columns]
    final = [dict(zip(columns, payment_type)) for payment_type in results]
    db.close()
    return final


def convert_to_parquet(result, filename):
    df = pd.DataFrame(result)
    df.to_parquet(filename, index=False)


def get_table_names():
    query = """
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public';"""
    db = connect_to_db()
    results = db.run(query)
    table_names = [row[0] for row in results if row != ['_prisma_migrations']]
    db.close()
    return table_names

def save_datetime_parameter(now):
    client = boto3.client("ssm")
    client.put_parameter(
        Name='latest-extract',
        Type = 'String',
        Value=str(now),
        Overwrite=True
    )

def retrieve_datetime_parameter():
    client = boto3.client("ssm")
    extract_datetime=client.get_parameter(
        Name='latest-extract'
    )
    return extract_datetime['Parameter']['Value']

def list_bucket_objects():
    client = boto3.client('s3')
    bucket_objects = client.list_objects_v2(
        Bucket=BUCKET_NAME
    )
    return bucket_objects['KeyCount']
   


def full_fetch(fetch_date=None):
    bucket_name = BUCKET_NAME
    client = boto3.client('s3')
    table_names = get_table_names()

    for name in table_names:
        single_table = get_single_table(name,fetch_date)

        if single_table:
            filename = f'{name}.parquet'
            key = name + '/' + year + '/' + month + '/' + day + '/' + time + '/' + name + '.parquet'

            convert_to_parquet(single_table, filename)

            result = client.upload_file(
                filename, bucket_name, key
            )
            logger.info(f"{name} files added to s3 bucket")

    
        


def lambda_handler(event=None, context=None):

    object_count = list_bucket_objects()

    if object_count > 0:
        last_fetch_datetime = retrieve_datetime_parameter()
        fetch_result = full_fetch(last_fetch_datetime)
        if not fetch_result:
            logger.info("No new files have been added to the database at this stage")
       
    else:
        full_fetch()
        logger.info("Full fetch of files from database")

    

    save_datetime_parameter(now)


lambda_handler()


 
 






