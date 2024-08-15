from pg8000.native import Connection
import boto3
import pandas as pd
import os


BUCKET_NAME = os.environ['DATA_PROCESSED_BUCKET_NAME']


def get_warehouse_credentials() -> dict:
    '''returns credentials for the data warehouse as dictionary

    Retuns:
        dictionary of aws credentials to access the data warehouse
    '''

    pass



def get_latest_data_for_one_table(object_key: str) -> list[dict]:
    '''reads parquet file at given key and returns list of dictionaries

    Args:
        object_key(string): key of a parquet file in transform bucket

    Returns:
        list with one dictionary for each row in the table 
    '''
    
    pass


def db_connection() -> Connection:
    '''returns connection to the data warehouse'''

    pass


def insert_new_data_into_data_warehouse(data: dict, object_key: str):
    '''inserts data from dictionary into a table in the data warehouse 

    Args:
        data(dict): dictionary of data to be inserted into the warehouse
        object_key(str): the table name

    '''

    pass


def lambda_handler(event: list, context):
    '''adds data from new parquet files in transform bucket to data warehouse

    Args:
        event(list) - list of updated tables
        {}
        context(json dict) - not used

    loops through all new parquet files in transform s3 and inserts data into
    corresponding table in the data warehouse.
    '''


    return {{
        'statusCode': 200,
        'body': 'Hello test lambda!'
    }}

