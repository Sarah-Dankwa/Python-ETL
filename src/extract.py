from pg8000.native import Connection, identifier, literal
from pg8000.exceptions import DatabaseError, InterfaceError
from botocore.exceptions import ClientError
import boto3
import json
import pandas as pd
import os
from datetime import datetime
import logging
import pytz 

logger = logging.getLogger() 

logging.getLogger().setLevel(logging.INFO)

BUCKET_NAME = os.environ.get('DATA_INGESTED_BUCKET_NAME')
uk_time = pytz.timezone('Europe/London')
now = datetime.now(uk_time)
year = now.strftime('%Y')
month = now.strftime('%m')
day = now.strftime('%d')
time = now.strftime('%H:%M:%S')


def get_database_credentials():
    secret_name = "totesys-database"
    client = boto3.client("secretsmanager")
    try:
        get_secret_value = client.get_secret_value(SecretId=secret_name)
        secret = get_secret_value["SecretString"]
        secret_dict = json.loads(secret)
        return secret_dict

    except client.exceptions.ResourceNotFoundException as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
             logger.error(f"The database [{secret_name}] could not be found")
        


def connect_to_db():
    try:
        secret = get_database_credentials()
        return Connection(
            user=secret["Username"],
            database=secret["Database"],
            password=secret["Password"],
            host=secret["Hostname"],
            port=secret["Port"]
        )
    except InterfaceError as e:
        logger.error("NO CONNECTION TO DATABASE - PLEASE CHECK")


def get_single_table(table_name, fetch_date=None):
    db = None
    try:
        db = connect_to_db()
        query = f"SELECT * FROM {identifier(table_name)}"

        if fetch_date:
            query += f" WHERE last_updated between {literal(fetch_date)} and {literal(str(now))};"    
        
        results = db.run(query)
        columns = [col["name"] for col in db.columns]
        final = [dict(zip(columns, payment_type)) for payment_type in results]
        return final
    
    except (DatabaseError, ClientError, InterfaceError, AttributeError) as e:
        logger.error(f"Error: {e}")

    finally:
        if db:
            db.close()

def convert_to_parquet(result, filename):
    df = pd.DataFrame(result)
    df.to_parquet(filename, index=False)


def get_table_names():
    db = None
    table_names = []
    try:
        db = connect_to_db()
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public';"""

        results = db.run(query)
        table_names = [row[0] for row in results if row != ['_prisma_migrations']]
        
    except (DatabaseError, AttributeError) as e:

        logger.error("Tables names cannot be accessed")

    finally:
        if db:
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
    try:
        extract_datetime=client.get_parameter(
            Name='latest-extract'
        )
        return extract_datetime['Parameter']['Value']
    
    except ClientError as e:
        logger.error(f"Could not retrieve date parameter: {e}") 

def list_bucket_objects():

    client = boto3.client('s3')
    bucket_objects = client.list_objects_v2(
        Bucket=BUCKET_NAME
    )
    return bucket_objects['KeyCount']
   


def fetch_from_db(fetch_date=None):
    bucket_name = BUCKET_NAME
    client = boto3.client('s3')
    table_names = get_table_names()
    udpated_tables = []

    if len(table_names) < 11:
        logger.error(f"There are {len(table_names)} tables fetched from the database - please check.")
        
    elif len(table_names) > 11:
        logger.warn("A table has been added to the database")

    else:
   
        for name in table_names:
            single_table = get_single_table(name,fetch_date)


            if single_table:
                filename = f'/tmp/{name}.parquet'
                key = name + '/' + year + '/' + month + '/' + day + '/' + time + '/' + name + '.parquet'
                udpated_tables.append(key)
                
                convert_to_parquet(single_table, filename)

                client.upload_file(
                    filename, bucket_name, key
                )
                logger.info(f"{name} files added to s3 bucket")

    
    return udpated_tables     


def lambda_handler(event=None, context=None):

    if not BUCKET_NAME:
        logger.error("BUCKET NOT FOUND - PLEASE CHECK")

    object_count = list_bucket_objects()

    if object_count > 0:
        last_fetch_datetime = retrieve_datetime_parameter()
        fetch_result = fetch_from_db(last_fetch_datetime)
        if not fetch_result:
            logger.info("No new files have been added to the database at this stage")
       
    else:
        fetch_result = fetch_from_db()
        logger.info("Full fetch of files from database")
        

    save_datetime_parameter(now)
    return fetch_result

   




 
 

