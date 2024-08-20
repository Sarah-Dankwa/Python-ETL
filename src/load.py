from pg8000.native import Connection, InterfaceError
import boto3
import pandas as pd
import os
import json
import logging


BUCKET_NAME = os.environ["DATA_PROCESSED_BUCKET_NAME"]

logger = logging.getLogger()
logging.getLogger().setLevel(logging.INFO)


def get_warehouse_credentials() -> dict:
    """returns credentials for the data warehouse as dictionary

    Retuns:
        dictionary of aws credentials to access the data warehouse
    """

    secret_name = "totesys-warehouse"
    client = boto3.client("secretsmanager")
    try:
        get_secret_value = client.get_secret_value(SecretId=secret_name)
        secret = get_secret_value["SecretString"]
        secret_dict = json.loads(secret)
        return secret_dict

    except client.exceptions.ResourceNotFoundException as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            logger.error(f"The database [{secret_name}] could not be found")


def db_connection() -> Connection:
    '''This function connects to the data warehouse hosted in the cloud
    using the credentials stored in aws.
    It logs an error if the connection fails.'''

    try:
        secret = get_warehouse_credentials()
        return Connection(
            user=secret["Username"],
            database=secret["Database"],
            password=secret["Password"],
            host=secret["Hostname"],
            port=secret["Port"],
        )
    except InterfaceError as e:
        logger.error("NO CONNECTION TO DATABASE - PLEASE CHECK")


def get_latest_data_for_one_table(object_key: str) -> list[dict]:
    """reads parquet file at given key and returns list of dictionaries

    Args:
        object_key(string): key of a parquet file in transform bucket

    Returns:
        list with one dictionary for each row in the table
    """
    
    pass


def insert_new_data_into_data_warehouse(data: list, object_key: str):
    """inserts data from dictionary into a table in the data warehouse

    Args:
        data(dict): dictionary of data to be inserted into the warehouse
        object_key(str): the table name

    """

    pass


def lambda_handler(event: list, context):
    """adds data from new parquet files in transform bucket to data warehouse

    Args:
        event(list) - list of updated tables
        {}
        context(json dict) - not used

    loops through all new parquet files in transform s3 and inserts data into
    corresponding table in the data warehouse.
    """

    return {"statusCode": 200, "body": "Hello test lambda!"}
