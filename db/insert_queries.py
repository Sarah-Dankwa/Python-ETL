from pg8000.native import identifier, literal
from db.oltp_data.address import address
from db.oltp_data.counterparty import counterparty
from db.oltp_data.currency import currency
from db.oltp_data.department import department
from db.oltp_data.design import design
from db.oltp_data.payment_type import payment_type
from db.oltp_data.payment import payment
from db.oltp_data.purchase_order import purchase_order
from db.oltp_data.sales_order import sales_order
from db.oltp_data.staff import staff
from db.oltp_data.transaction import transaction


def get_insert_query(table: str, data: list) -> str:
    """returns an SQL insert query for the given data

    Args:
        table(str): name of the table to create the query for
        data(list): a list of dictionaries with the data to be inserted
    Returns SQL query string
    """

    columns = [identifier(col) for col in data[0].keys()]
    data_list = []
    for row in data:
        row_query = "("
        row_query += ", ".join([literal(data) for data in row.values()])
        row_query += ")"
        data_list.append(row_query)

    query = f"""
    INSERT INTO {identifier(table)} (
    {', '. join(columns)}
    ) VALUES
    {', '.join(data_list)}"""
    return query


def get_all_insert_queries() -> list:
    """constructs insert queries for all tables in the test oltp database

    gets data from files in db/oltp_data/
    runs get_insert_query for every table in the database.

    Returns:
        list of insert queries for every table
    """

    all_data = [
        payment_type,
        design,
        currency,
        department,
        staff,
        address,
        counterparty,
        purchase_order,
        sales_order,
        transaction,
        payment,
    ]
    tables = [
        "payment_type",
        "design",
        "currency",
        "department",
        "staff",
        "address",
        "counterparty",
        "purchase_order",
        "sales_order",
        "transaction",
        "payment",
    ]
    all_queries = [
        get_insert_query(table, data) for table, data in zip(tables, all_data)
    ]
    return all_queries
