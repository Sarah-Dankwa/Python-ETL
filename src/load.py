from pg8000.native import Connection, identifier, literal
from pg8000.exceptions import DatabaseError, InterfaceError
from botocore.exceptions import ClientError
import boto3
import pandas as pd
import os
import json
import logging
from io import BytesIO


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
    except InterfaceError:
        logger.error("NO CONNECTION TO DATABASE - PLEASE CHECK")


def get_latest_data_for_one_table(object_key: str) -> list:
    """reads parquet file at given key and returns dataframe

    Args:
        object_key(string): key of a parquet file in transform bucket

    Returns:
        dataframe with data from table
    """

    s3 = boto3.client('s3')
    try:
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=object_key)
        # reads the content of the s3 object as a binary stream
        buffer = BytesIO(obj['Body'].read())
        # saves buffer object to pandas dataframe
        df = pd.read_parquet(buffer) 
        return df
    except ClientError as e:
        logger.error(
            f"Cannot access the parquet file in the processed data bucket: {e}"
        )


def insert_new_data_into_data_warehouse(df: pd.DataFrame, table_name: str):
    """inserts data from dataframe into a table in the data warehouse

    Args:
        data(dict): dataframe of data to be inserted into the warehouse
        table_name(str): the table name

    """

    # identifier prevents sql injection for table names & column names
    query = f"INSERT INTO {identifier(table_name)} ("
    # converts column names from df to 'col, col, col...' & adds to query
    query += ', '.join([identifier(col) for col in df.columns])
    query += ') VALUES '
    insert_list = []

    # creates '(value, value, value...)' for each row in df 
    # then appends to insert list - literal prevents sql injection for values
    for row in df.values:
        row_query = '('
        row_query += ', '.join([literal(value) for value in row])
        row_query += ')'
        insert_list.append(row_query)
    
    # converts insert_list to a string with commas separating each element
    # then adds to query
    query += ', '.join(insert_list)
    query += ';'
    conn = None
    try:
        conn = db_connection()
        conn.run(query)
    except (DatabaseError, AttributeError) as e:
        logger.error(f"Cannot add data to the database: {e}")

    finally:
        if conn:
            conn.close()



def lambda_handler(event: list, context):
    """adds data from new parquet files in transform bucket to data warehouse

    Args:
        event(list) - list of keys of parquet files in transform bucket
        context(json dict) - not used

    loops through all new parquet files in transform s3 and inserts data into
    corresponding table in the data warehouse.
    """

    for key in event:
        df = get_latest_data_for_one_table(key)
        if df:
            table_name = key.split('/')[0]
            insert_new_data_into_data_warehouse(df, table_name)
