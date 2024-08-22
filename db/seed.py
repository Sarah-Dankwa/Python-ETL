from pg8000.native import identifier, Connection

def seed_warehouse(db: Connection):
    """adds empty tables to the warehouse

    Args: 
        db - database connection
    """
    tables = [
        'dim_date',
        'dim_staff',
        'dim_location',
        'dim_currency',
        'dim_design',
        'dim_counterparty',
        'fact_sales_order',
    ]

    for table in tables:
        db.run(f'DROP TABLE IF EXISTS {identifier(table)};')
    
    queries = get_queries()
    for query in queries:
        db.run(query)


def get_queries():
    '''queries to create expected tables in mock data warehouse'''

    fact_sales_order = '''
    CREATE TABLE fact_sales_order (
        sales_record_id SERIAL PRIMARY KEY,
        sales_order_id INT NOT NULL,
        created_date DATE NOT NULL,
        created_time TIME NOT NULL,
        last_updated_date DATE NOT NULL,
        last_updated_time TIME NOT NULL,
        sales_staff_id INT NOT NULL,
        counterparty_id INT NOT NULL,
        units_sold INT NOT NULL,
        unit_price NUMERIC(10, 2) NOT NULL,
        currency_id INT NOT NULL,
        design_id INT NOT NULL,
        agreed_payment_date DATE NOT NULL,
        agreed_delivery_date DATE NOT NULL,
        agreed_delivery_location_id INT NOT NULL
    );
    '''

    dim_date = '''
    CREATE TABLE dim_date (
        date_id DATE PRIMARY KEY NOT NULL,
        year INT NOT NULL,
        month INT NOT NULL,
        day INT NOT NULL,
        day_of_week INT NOT NULL,
        day_name VARCHAR NOT NULL,
        month_name VARCHAR NOT NULL,
        quarter INT NOT NULL
    );
    '''

    dim_staff = '''
    CREATE TABLE dim_staff (
        staff_id INT NOT NULL,
        first_name VARCHAR NOT NULL,
        last_name VARCHAR,
        department_name VARCHAR NOT NULL,
        location VARCHAR NOT NULL,
        email_address VARCHAR NOT NULL
    );'''

    dim_location = '''
    CREATE TABLE dim_location (
        location_id INT PRIMARY KEY NOT NULL,
        address_line_1 VARCHAR NOT NULL,
        address_line_2 VARCHAR,
        district VARCHAR,
        city VARCHAR NOT NULL,
        postal_code VARCHAR NOT NULL,
        country VARCHAR NOT NULL,
        phone VARCHAR NOT NULL
    );
    '''

    dim_currency = '''
    CREATE TABLE dim_currency (
        currency_id INT PRIMARY KEY NOT NULL,
        currency_code VARCHAR NOT NULL,
        currency_name VARCHAR NOT NULL
    );
    '''

    dim_design='''
    CREATE TABLE dim_design(
        design_id int PRIMARY KEY NOT NULL,
        design_name VARCHAR NOT NULL,
        file_location VARCHAR NOT NULL,
        file_name VARCHAR NOT NULL
    );
    '''

    dim_counterparty = '''
    CREATE TABLE dim_counterparty (
        counterparty_id INT PRIMARY KEY NOT NULL,
        counterparty_legal_name VARCHAR NOT NULL,
        counterparty_legal_address_line_1 VARCHAR NOT NULL,
        counterparty_legal_address_line2 VARCHAR,
        counterparty_legal_district VARCHAR,
        counterparty_legal_city VARCHAR NOT NULL,
        counterparty_legal_postal_code VARCHAR NOT NULL,
        counterparty_legal_country VARCHAR NOT NULL,
        counterparty_legal_phone_number VARCHAR NOT NULL
    );'''

    return [
        fact_sales_order,
        dim_date,
        dim_staff,
        dim_location,
        dim_currency,
        dim_design,
        dim_counterparty
    ]