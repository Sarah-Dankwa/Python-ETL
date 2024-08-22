def get_oltp_queries():
    
    payment_type = """
    CREATE TABLE payment_type (
        payment_type_id SERIAL PRIMARY KEY NOT NULL,
        payment_type_name VARCHAR NOT NULL,
        created_at TIMESTAMP NOT NULL,
        last_updated TIMESTAMP NOT NULL
    );"""

    design = """
    CREATE TABLE design (
        design_id SERIAL PRIMARY KEY NOT NULL,
        created_at TIMESTAMP NOT NULL,
        last_updated TIMESTAMP NOT NULL,
        design_name VARCHAR NOT NULL,
        file_location VARCHAR NOT NULL,
        file_name VARCHAR NOT NULL
    );"""

    currency = """
    CREATE TABLE currency (
        currency_id SERIAL PRIMARY KEY NOT NULL,
        currency_code CHAR(3) NOT NULL,
        created_at TIMESTAMP NOT NULL,
        last_updated TIMESTAMP NOT NULL
    );"""

    department = """
    CREATE TABLE department (
        department_id SERIAL PRIMARY KEY NOT NULL,
        department_name VARCHAR NOT NULL,
        location VARCHAR,
        manager VARCHAR,
        created_at TIMESTAMP NOT NULL,
        last_updated TIMESTAMP NOT NULL
    );"""
    
    staff = """
    CREATE TABLE staff (
        staff_id SERIAL PRIMARY KEY NOT NULL,
        first_name VARCHAR NOT NULL,
        last_name VARCHAR NOT NULL,
        department_id INT NOT NULL REFERENCES department,
        email_address VARCHAR NOT NULL,
        created_at TIMESTAMP NOT NULL,
        last_updated TIMESTAMP NOT NULL
    );"""

    address = """
    CREATE TABLE address (
        address_id SERIAL PRIMARY KEY NOT NULL,
        address_line_1 VARCHAR NOT NULL,
        address_line_2 VARCHAR,
        district VARCHAR,
        city VARCHAR NOT NULL,
        postal_code VARCHAR NOT NULL,
        country VARCHAR NOT NULL,
        phone VARCHAR NOT NULL,
        created_at TIMESTAMP NOT NULL,
        last_updated TIMESTAMP NOT NULL
    );"""

    counterparty = """
    CREATE TABLE counterparty (
        counterparty_id SERIAL PRIMARY KEY NOT NULL,
        counterparty_legal_name VARCHAR NOT NULL,
        legal_address_id INT NOT NULL REFERENCES address,
        commercial_contact VARCHAR,
        delivery_contact VARCHAR,
        created_at TIMESTAMP NOT NULL,
        last_updated TIMESTAMP NOT NULL
    );"""

    purchase_order = """
    CREATE TABLE purchase_order (
        purchase_order_id SERIAL PRIMARY KEY NOT NULL,
        created_at TIMESTAMP NOT NULL,
        last_updated TIMESTAMP NOT NULL,
        staff_id INT NOT NULL REFERENCES staff,
        counterparty_id INT NOT NULL REFERENCES counterparty,
        item_code VARCHAR NOT NULL,
        item_quantity INT NOT NULL,
        item_unit_price NUMERIC NOT NULL,
        currency_id INT NOT NULL REFERENCES currency,
        agreed_delivery_date DATE NOT NULL,
        agreed_payment_date DATE NOT NULL,
        agreed_delivery_location_id INT NOT NULL REFERENCES address
    );"""

    sales_order = """
    CREATE TABLE sales_order (
        sales_order_id SERIAL PRIMARY KEY NOT NULL,
        created_at TIMESTAMP NOT NULL,
        last_updated TIMESTAMP NOT NULL,
        design_id INT NOT NULL REFERENCES design,
        staff_id INT NOT NULL REFERENCES staff,
        counterparty_id INT NOT NULL REFERENCES counterparty,
        units_sold INT NOT NULL,
        unit_price NUMERIC NOT NULL,
        currency_id INT NOT NULL REFERENCES currency,
        agreed_delivery_date DATE NOT NULL,
        agreed_payment_date DATE NOT NULL,
        agreed_delivery_location_id INT REFERENCES address
    );"""

    transaction = """
    CREATE TABLE transaction (
        transaction_id SERIAL PRIMARY KEY NOT NULL,
        transaction_type VARCHAR NOT NULL,
        sales_order_id INT REFERENCES sales_order,
        purchase_order_id INT REFERENCES purchase_order,
        created_at TIMESTAMP NOT NULL,
        last_updated TIMESTAMP NOT NULL
    );"""

    payment = """
    CREATE TABLE payment (
        payment_id SERIAL PRIMARY KEY NOT NULL,
        created_at TIMESTAMP NOT NULL,
        last_updated TIMESTAMP NOT NULL,
        transaction_id INT NOT NULL REFERENCES transaction,
        counterparty_id INT NOT NULL REFERENCES counterparty,
        payment_amount NUMERIC NOT NULL,
        currency_id INT NOT NULL REFERENCES currency,
        payment_type_id INT NOT NULL REFERENCES payment_type,
        paid boolean NOT NULL,
        payment_date DATE NOT NULL,
        company_ac_number INT NOT NULL,
        counterparty_ac_number INT NOT NULL
    );"""

    return [
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
        payment
    ]

def get_warehouse_queries():
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
        counterparty_legal_address_line_2 VARCHAR,
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