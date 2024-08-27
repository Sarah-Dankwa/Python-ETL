from botocore.exceptions import ClientError
import boto3
import json
import pandas as pd
import os
from datetime import datetime
import logging
import pytz
import io
from forex_python.converter import CurrencyCodes

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
    """
    This function takes list of keys of S3 path and returns DataFrame from parquet file correspdonding to each key
    """
    try:
        if s3_client is None:
            s3_client = boto3.client("s3")
        dfs = []
        for key in keys:
            obj = s3_client.get_object(Bucket=INGEST_BUCKET_NAME, Key=key)
            dfs.append(pd.read_parquet(io.BytesIO(obj["Body"].read())))

        final = pd.concat(dfs, ignore_index=True)
        return final

    except Exception as e:
        logger.error(f"Error{e} Key not found in S3")


def write_parquet_to_s3_bucket(df, prefix, s3_client=None):
    """
    This function takes in DataFrame and file prefix, writes corresponding parquet file to S3 bucket
    """
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


def dim_date(start="2021-01-01", end="2024-12-31"):
    """
    This function takes start and end date time and creates a DataFrame with specific columns for that date range
    """
    try:
        df = pd.DataFrame({"date_id": pd.date_range(start, end)})
        df["day_name"] = df.date_id.dt.strftime("%A")
        df["day"] = df.date_id.dt.day
        df["day_of_week"] = df.date_id.dt.day_of_week
        df["month"] = df.date_id.dt.month
        df["month_name"] = df.date_id.dt.strftime("%B")
        df["quarter"] = df.date_id.dt.quarter
        df["year"] = df.date_id.dt.year
        df["date_id"] = df["date_id"].dt.strftime("%Y-%m-%d")
        return df
    except Exception as e:
        logger.error(f"Error{e} while creating a date dimension table")


def fact_sales_order(sales_order_df):
    """
    This function takes in sales_order DataFrame and creates fact_sales_order DataFrame
    """
    try:
        fact_sales_order_df = pd.DataFrame()
        fact_sales_order_df = sales_order_df[
            [
                "sales_order_id",
                "created_at",
                "last_updated",
                "staff_id",
                "counterparty_id",
                "units_sold",
                "unit_price",
                "currency_id",
                "design_id",
                "agreed_delivery_date",
                "agreed_payment_date",
                "agreed_delivery_location_id",
            ]
        ]
        fact_sales_order_df["created_date"] = fact_sales_order_df["created_at"].dt.date
        fact_sales_order_df["created_time"] = fact_sales_order_df["created_at"].dt.time
        fact_sales_order_df["last_updated_date"] = fact_sales_order_df[
            "last_updated"
        ].dt.date
        fact_sales_order_df["last_updated_time"] = fact_sales_order_df[
            "last_updated"
        ].dt.time
        df = fact_sales_order_df.drop(["created_at", "last_updated"], axis=1)
        df.rename(columns={"staff_id": "sales_staff_id"}, inplace=True)
        return df
    except Exception as e:
        logger.error(f"Error{e} failed to create fact_sales_order dataframe")


def dim_design(design_df):
    """
    This function takes in design DataFrame and creates dim_design DataFrame
    """
    try:
        dim_design_df = pd.DataFrame()
        dim_design_df = design_df[
            ["design_id", "design_name", "file_location", "file_name"]
        ]

        return dim_design_df
    except Exception as e:
        logger.error(f"Error{e} failed to create dim_design dataframe")


def dim_currency(currency_df):
    """
    This function takes in currency DataFrame and creates dim_currency DataFrame. Also uses get_currency_name to fetch the currency name using currency code.
    """
    try:
        dim_currency_df = pd.DataFrame()
        dim_currency_df = currency_df[["currency_id", "currency_code"]]
        c = CurrencyCodes()
        dim_currency_df["currency_name"] = dim_currency_df["currency_code"].apply(
            c.get_currency_name
        )
        return dim_currency_df
    except Exception as e:
        logger.error(f"Error{e} failed to create dim_currency dataframe")


def get_all_files(prefix, s3_client=None):
    """
    This function takes file path prefix in S3 folder and returns all .parquet file paths in that S3 folder
    """
    try:
        file_path_list = []
        if s3_client is None:
            s3_client = boto3.client("s3")
        response = s3_client.list_objects_v2(Bucket=INGEST_BUCKET_NAME, Prefix=prefix)
        for path in response["Contents"]:
            if ".parquet" in path["Key"]:
                file_path_list.append(path["Key"])
        return file_path_list
    except Exception as e:
        logger.error(f"Error{e} failed to load files")


def dim_staff(staff_df):
    """
    This function takes in staff DataFrame and creates dim_staff DataFrame by referencing
    entire department DataFrame and join with latest staff DataFrame
    """
    try:

        list_files = get_all_files("department")
        department_df = read_parquet_from_s3(list_files)
        staff_department_df = pd.merge(
            staff_df,
            department_df[["department_id", "location", "department_name"]],
            on="department_id",
            how="left",
        )
        dim_staff_df = pd.DataFrame()
        dim_staff_df = staff_department_df[
            [
                "staff_id",
                "first_name",
                "last_name",
                "department_name",
                "location",
                "email_address",
            ]
        ]
        return dim_staff_df
    except Exception as e:
        logger.error(f"Error{e} failed to create dim_staff dataframe")


def dim_counterparty(counterparty_df):
    """
    This function takes in counterparty DataFrame and creates dim_counterparty DataFrame by referencing
    entire address DataFrame and join with latest counterparty DataFrame
    """
    try:
        list_files = get_all_files("address")
        address_df = read_parquet_from_s3(list_files)
        counterparty_address_df = pd.merge(
            counterparty_df,
            address_df,
            left_on="legal_address_id",
            right_on="address_id",
            how="left",
        )
        dim_counterparty_df = pd.DataFrame()
        dim_counterparty_df = counterparty_address_df[
            [
                "counterparty_id",
                "counterparty_legal_name",
                "address_line_1",
                "address_line_2",
                "district",
                "city",
                "postal_code",
                "country",
                "phone",
            ]
        ]
        dim_counterparty_df.rename(
            columns={
                "address_line_1": "counterparty_legal_address_line_1",
                "address_line_2": "counterparty_legal_address_line_2",
                "district": "counterparty_legal_district",
                "city": "counterparty_legal_city",
                "postal_code": "counterparty_legal_postal_code",
                "country": "counterparty_legal_country",
                "phone": "counterparty_legal_phone_number",
            },
            inplace=True,
        )
        return dim_counterparty_df
    except Exception as e:
        logger.error(f"Error{e} failed to create dim_counterparty dataframe")


def dim_location(address_df):
    """
    This function takes in address DataFrame and creates dim_location DataFrame
    """
    try:
        dim_location_df = address_df[
            [
                "address_id",
                "address_line_1",
                "address_line_2",
                "district",
                "city",
                "postal_code",
                "country",
                "phone",
            ]
        ]
        dim_location_df.rename(columns={"address_id": "location_id"}, inplace=True)
        return dim_location_df
    except Exception as e:
        logger.error(f"Error{e} failed to create dim_location dataframe")


def lambda_handler(event=None, context=None):

    """
    1. Extratc Lambda outputs the list of files added to the extract s3 bucket
    2. Based on the list of parquete files from Extract Lambda, Read the parquete from extract S3 bucket one by one
    3. Merge all the parqetes and create one single dataframe(Master) (for now specific fact_sales_order schema)
    4. Create fact_sales_order dataframe using Master dataframe
    5. Create dim_staff dataframe by using Master dataframe
    6. Create fact_sales_order dataframe by using Master dataframe

    postgres Fact and Dimention table dependancy tables from the Totesys database
    dim_counterparty -> counterparty and address
    dim_date -> standalone
    dim_staff -> staff and department
    dim_location -> address and sales_order
    dim_currency -> currency
    dim_design -> design
    fact_sales_order -> sales_order, dim_design, dim_currency, dim_location, dim_staff, dim_date and dim_counterparty
    """
    try:
        file_path_list = []
        client = boto3.client("s3")
        date_objects = client.list_objects_v2(
            Bucket=TRANSFORM_BUCKET_NAME, Prefix="dim_date"
        )
        bucket_objects = client.list_objects_v2(Bucket=TRANSFORM_BUCKET_NAME)
        if bucket_objects["KeyCount"] == 0:

            # creation of dimension location
            location_files = get_all_files("address")
            location_df = read_parquet_from_s3(location_files)
            file_path_list.append(
                write_parquet_to_s3_bucket(dim_location(location_df), "dim_location")
            )

            # creation of dimension counterparty
            counterparty_files = get_all_files("counterparty")
            counterparty_df = read_parquet_from_s3(counterparty_files)
            file_path_list.append(
                write_parquet_to_s3_bucket(
                    dim_counterparty(counterparty_df), "dim_counterparty"
                )
            )

            # creation of dimension staff
            staff_files = get_all_files("staff")
            staff_df = read_parquet_from_s3(staff_files)
            file_path_list.append(
                write_parquet_to_s3_bucket(dim_staff(staff_df), "dim_staff")
            )

            # creation of dimension currency
            currency_files = get_all_files("currency")
            currency_df = read_parquet_from_s3(currency_files)
            file_path_list.append(
                write_parquet_to_s3_bucket(dim_currency(currency_df), "dim_currency")
            )

            # creation of dimension design
            design_files = get_all_files("design")
            design_df = read_parquet_from_s3(design_files)
            file_path_list.append(
                write_parquet_to_s3_bucket(dim_design(design_df), "dim_design")
            )

            # creation of dimension date
            file_path_list.append(write_parquet_to_s3_bucket(dim_date(), "dim_date"))

            # creation of fact saler_order
            sales_order_files = get_all_files("sales_order")
            sales_order_df = read_parquet_from_s3(sales_order_files)
            file_path_list.append(
                write_parquet_to_s3_bucket(
                    fact_sales_order(sales_order_df), "fact_sales_order"
                )
            )

            logger.info(f"Fetching all files and transforming all tables completed")
            return file_path_list

        elif date_objects["KeyCount"] == 0:
            # creation of dimension date
            file_path_list.append(write_parquet_to_s3_bucket(dim_date(), "dim_date"))
            logger.info(f"Fetching date dimension has been updated")
            return file_path_list

        elif event == []:
            logger.info(f"No new files to transfrom")
            return file_path_list

        else:
            for key in event:
                if key.split("/")[0] == "address":
                    location_df = read_parquet_from_s3([key])
                    file_path_list.append(
                        write_parquet_to_s3_bucket(
                            dim_location(location_df), "dim_location"
                        )
                    )

                elif key.split("/")[0] == "counterparty":
                    counterparty_df = read_parquet_from_s3([key])
                    file_path_list.append(
                        write_parquet_to_s3_bucket(
                            dim_counterparty(counterparty_df), "dim_counterparty"
                        )
                    )

                elif key.split("/")[0] == "staff":
                    staff_df = read_parquet_from_s3([key])
                    file_path_list.append(
                        write_parquet_to_s3_bucket(dim_staff(staff_df), "dim_staff")
                    )

                elif key.split("/")[0] == "currency":
                    currency_df = read_parquet_from_s3([key])
                    file_path_list.append(
                        write_parquet_to_s3_bucket(
                            dim_currency(currency_df), "dim_currency"
                        )
                    )

                elif key.split("/")[0] == "design":
                    design_df = read_parquet_from_s3([key])
                    file_path_list.append(
                        write_parquet_to_s3_bucket(dim_design(design_df), "dim_design")
                    )

                elif key.split("/")[0] == "sales_order":
                    sales_order_df = read_parquet_from_s3([key])
                    file_path_list.append(
                        write_parquet_to_s3_bucket(
                            fact_sales_order(sales_order_df), "fact_sales_order"
                        )
                    )
                else:
                    logger.info(f"{key} not handled in current schema")

            logger.info(f"Fetching all files and transforming all tables completed")
            return file_path_list
    except Exception as e:
        logger.error(f"Error{e} Transform lambda failed to complete")
