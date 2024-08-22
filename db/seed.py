from pg8000.native import identifier, Connection
from db.create_queries import get_warehouse_queries, get_oltp_queries
from db.insert_queries import get_all_insert_queries

def seed(db: Connection, queries: list, insert_queries:list = None):
    tables = get_warehouse_tables()
    tables += get_oltp_tables()

    teardown(db, tables)
    for query in queries:
        db.run(query)
    
    if insert_queries:
        for query in insert_queries:
            db.run(query)


def teardown(db: Connection, tables: list):
    for table in tables:
        db.run(f'DROP TABLE IF EXISTS {identifier(table)};')


def seed_warehouse(db: Connection):
    """adds empty tables to the warehouse

    Args: 
        db - database connection
    """
    queries = get_warehouse_queries()
    seed(db, queries)


def seed_oltp(db: Connection):
    queries = get_oltp_queries()
    insert_queries = get_all_insert_queries()
    seed(db, queries, insert_queries)


def get_oltp_tables():
    return [
        'payment',
        'transaction',
        'sales_order',
        'purchase_order',
        'counterparty',
        'address',
        'staff', 
        'department',
        'currency',
        'design',
        'payment_type'
    ]
    
    
def get_warehouse_tables():
    return [
        'dim_date',
        'dim_staff',
        'dim_location',
        'dim_currency',
        'dim_design',
        'dim_counterparty',
        'fact_sales_order',
    ]

