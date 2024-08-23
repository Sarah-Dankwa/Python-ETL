from pg8000.native import Connection, identifier, literal
from pg8000.exceptions import DatabaseError, InterfaceError
from botocore.exceptions import ClientError
import boto3
import pandas as pd
import os
import json
import logging
import traceback
from io import BytesIO

BUCKET_NAME = os.environ["DATA_PROCESSED_BUCKET_NAME"]
SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]

logger = logging.getLogger()
logging.getLogger().setLevel(logging.INFO)

sns_client = boto3.client('sns')
# SNS_TOPIC_ARN = "arn:aws:sns:eu-west-2:590183674561:totesys-workflow-step-functions-notifications"
# SNS_TOPIC_ARN = "arn:aws:sns:eu-west-2:026090521693:totesys-workflow-step-functions-notifications"



def send_sns_notification(message: str):
    """Send SNS notification with detailed error message"""
    try:
        logger.info(f"SNS_TOPIC_ARN: {SNS_TOPIC_ARN}")
        
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject="Error in Load Lambda Function"
        )
    except ClientError as e:
        logger.error(f"Failed to send SNS notification: {e}")


def format_error_message(error):

    # Extract the main components from the error
    error_message = error.get("errorMessage", "No error message provided.")
    error_type = error.get("errorType", "UnknownError")
    stack_trace = "\n".join(error.get("stackTrace", []))  # Formatting stack trace

    # Format a cleaner message
    formatted_message = f"""
    Error Type: {error_type}
    Error Message: {error_message}

    Stack Trace:
    {stack_trace}
    """
    return formatted_message

def get_warehouse_credentials() -> dict:
    secret_name = "totesys-warehouse"
    client = boto3.client("secretsmanager")
    try:
        get_secret_value = client.get_secret_value(SecretId=secret_name)
        secret = get_secret_value["SecretString"]
        return json.loads(secret)
    except client.exceptions.ResourceNotFoundException as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            error_msg = f"The database [{secret_name}] could not be found: {e}"
            logger.error(error_msg)

            send_sns_notification(error_msg)

            raise
            
def db_connection() -> Connection:
    """This function connects to the data warehouse hosted in the cloud
    using the credentials stored in aws.
    It logs an error if the connection fails."""

def db_connection() -> Connection:
    try:
        secret = get_warehouse_credentials()
        return Connection(
            user=secret["Username"],
            database=secret["Database"],
            password=secret["Password"],
            host=secret["Hostname"],
            port=secret["Port"]
        )
    except InterfaceError as e:
        error_msg = f"No connection to database - please check: {e}"
        logger.error(error_msg)

        send_sns_notification(error_msg)

        raise

def get_latest_data_for_one_table(object_key: str) -> pd.DataFrame:
    s3 = boto3.client('s3')
    try:
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=object_key)
        buffer = BytesIO(obj['Body'].read())
        df = pd.read_parquet(buffer)
        return df
    except ClientError as e:
        error_msg = f"Cannot access the parquet file in the processed data bucket: {e}"
        logger.error(error_msg)
        detailed_message = f"Key: {object_key}\nError: {e}\nStack Trace: {traceback.format_exc()}"

        send_sns_notification(detailed_message)

        raise

def insert_new_data_into_data_warehouse(df: pd.DataFrame, table_name: str):
    query = f"INSERT INTO {identifier(table_name)} ("
    query += ', '.join([identifier(col) for col in df.columns])
    query += ') VALUES '
    
    insert_list = []
    for row in df.values:
        row_query = '(' + ', '.join([literal(value) for value in row]) + ')'
        insert_list.append(row_query)
    query += ', '.join(insert_list) + ';'
    
    conn = None

    try:
        conn = db_connection()
        conn.run(query)
    except (DatabaseError, AttributeError) as e:
        error_msg = f"Cannot add data to the database: {e}"
        logger.error(error_msg)
        detailed_message = f"Table: {table_name}\nError: {e}\nStack Trace: {traceback.format_exc()}"

        send_sns_notification(detailed_message)
        raise

    finally:
        if conn:
            conn.close()

def lambda_handler(event: list, context):
    """Lambda handler to add data from S3 parquet files to data warehouse"""
    # for key in event:
    #     try:
    #         df = get_latest_data_for_one_table(key)
    #         if df is not None:
    #             table_name = key.split('/')[0]
    #             insert_new_data_into_data_warehouse(df, table_name)
    #     except Exception as e:
    #         # Ensure the Step Function gets an error response to handle it
    #         error_msg = f"Error processing key: {key}. Exception: {e}"
    #         logger.error(error_msg)
            
    #         detailed_message = f"{error_msg}\nStack Trace: {traceback.format_exc()}"

    #         send_sns_notification(detailed_message)

    #         raise  # Re-raise the exception for Step Function to catch it

    try:
        for key in event:
            df = get_latest_data_for_one_table(key)
            if df:
                table_name = key.split('/')[0]
                # insert_new_data_into_data_warehouse(df, table_name)
    except Exception as e:
        error_details = {
            "errorMessage": str(e),
            "errorType": type(e).__name__,
            "stackTrace": traceback.format_exc().splitlines()
        }

        formatted_message = format_error_message(error_details)
        logging.error(formatted_message)
        
        # Send formatted error message to SNS
        send_sns_notification(json.dumps(formatted_message))
        
        raise
