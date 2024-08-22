from pg8000.native import Connection, identifier, literal
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

def get_insert_query(table: str, data: list):
    columns = [identifier(col) for col in data[0].keys()]
    data_list = []
    for row in data:
        row_query = '('
        row_query += ', '.join([literal(data) for data in row.values()])
        row_query += ')'
        data_list.append(row_query)
    
    query = f"""
    INSERT INTO {identifier(table)} (
    {', '. join(columns)}
    ) VALUES 
    {', '.join(data_list)}"""
    return query

def get_all_insert_queries():
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
        payment
    ]
    tables = [
        'payment_type',
        'design',
        'currency',
        'department',
        'staff', 
        'address',
        'counterparty', 
        'purchase_order',
        'sales_order',
        'transaction',
        'payment'
    ]
    all_queries = [
        get_insert_query(table, data) for table, data in zip(tables,all_data)
    ]
    return all_queries