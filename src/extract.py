from pg8000.native import Connection, identifier
from botocore.exceptions import ClientError
import boto3
import json


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
        port=secret["Port"],
    )


def get_single_table(table_name):
    db = connect_to_db()
    query = f"SELECT * FROM {identifier(table_name)};"
    results = db.run(query)
    columns = [col["name"] for col in db.columns]
    final = [dict(zip(columns, payment_type)) for payment_type in results]
    db.close()
    return final


def full_fetch():
    # list of table names
    # for each table
    # run get_single table
    # convert to parquet
    # get timestamp
    # save to s3 on timestamp / tablename
    pass
