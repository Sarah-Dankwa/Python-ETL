from pg8000.native import Connection, identifier
from botocore.exceptions import ClientError
import boto3
import json
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import os
from datetime import datetime


# BUCKET_NAME = os.environ['BUCKET_NAME']
BUCKET_NAME = 'sarah-jessica-test-bucket'
now = datetime.now()
year = now.strftime('%Y')
month = now.strftime('%m')
day = now.strftime('%d')
time = now.strftime('%H:%M:%S')
print(str(now)[:-3])

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


def get_single_table(table_name):
    db = connect_to_db()
    query = f"SELECT * FROM {identifier(table_name)};"
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

def save_datetime_parameter():
    client = boto3.client("ssm")
    client.put_parameter(
        Name='latest-extract',
        Value=str(now)[:-3],
        Overwrite=True
    )


def retrieve_datetime_parameter():
    client = boto3.client("ssm")
    client.get_parameter(
        Name='latest-extract'
    )


def full_fetch():
    bucket_name = BUCKET_NAME
    client = boto3.client('s3')
    table_names = get_table_names()

    for name in table_names:
        single_table = get_single_table(name)
        filename = f'{name}.parquet'
        key = name + '/' + year + '/' + month + '/' + day + '/' + time + '/' + name + '.parquet'
        convert_to_parquet(single_table, filename)
        client.upload_file(
            filename, bucket_name, key
        )


def lambda_handler(event, context):
    pass

