from pg8000.native import identifier, Connection
from db.create_queries import get_warehouse_queries, get_oltp_queries
from db.insert_queries import get_all_insert_queries


def seed(db: Connection, queries: list, insert_queries: list = None):
    """removes existing tables in the databse and runs given queries

    Args:
        db - pg8000 connection
        queries - list of queries to create all the tables in the
            warehouse / oltp database
        insert queries - list of insert queries only needed for oltp database
    Returns None
    """

    tables = get_warehouse_tables()
    tables += get_oltp_tables()

    teardown_db(db, tables)
    for query in queries:
        db.run(query)

    if insert_queries:
        for query in insert_queries:
            db.run(query)


def teardown_db(db: Connection, tables: list):
    """removes the every table in the list of tables from the database.

    Args:
        db - pg8000 connection
        tables - list of table names to be removed
    Returns None
    """

    for table in tables:
        db.run(f"DROP TABLE IF EXISTS {identifier(table)};")


def seed_warehouse(db: Connection):
    """Runs seed function to populate the test warehouse

    gets list of create table queries from create_queries.py

    Args:
        db - pg8000 database connection
    """

    queries = get_warehouse_queries()
    seed(db, queries)


def seed_oltp(db: Connection):
    """Runs seed function to populate the test oltp database

    gets list of create table queries from create_queries.py
    and insert table queries from insert_queries.py

    Args:
        db - pg8000 database connection
    """

    queries = get_oltp_queries()
    insert_queries = get_all_insert_queries()
    seed(db, queries, insert_queries)


def get_oltp_tables():
    """returns a list of all tables in the oltp database"""

    return [
        "payment",
        "transaction",
        "sales_order",
        "purchase_order",
        "counterparty",
        "address",
        "staff",
        "department",
        "currency",
        "design",
        "payment_type",
    ]


def get_warehouse_tables():
    """returns a list of all tables in the data warehouse"""

    return [
        "dim_date",
        "dim_staff",
        "dim_location",
        "dim_currency",
        "dim_design",
        "dim_counterparty",
        "fact_sales_order",
    ]
