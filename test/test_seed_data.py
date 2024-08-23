from datetime import datetime, date
from decimal import Decimal

fact_sales_order_cols = [
    'sales_record_id', 'sales_order_id', 'created_date', 'created_time',
    'last_updated_date', 'last_updated_time', 'sales_staff_id',
    'counterparty_id', 'units_sold', 'unit_price', 'currency_id',
    'design_id',
    'agreed_payment_date',
    'agreed_delivery_date',
    'agreed_delivery_location_id'
]

dim_staff_cols = [
    'staff_id',
    'first_name',
    'last_name',
    'department_name',
    'location',
    'email_address'
]

dim_location_cols = [
    'location_id',
    'address_line_1',
    'address_line_2',
    'district',
    'city',
    'postal_code',
    'country',
    'phone',
]
dim_design_cols = [
    'design_id',
    'design_name',
    'file_location',
    'file_name'
]
dim_date_cols = [
    'date_id',
    'year',
    'month',
    'day',
    'day_of_week',
    'day_name',
    'month_name',
    'quarter'
]
dim_currency_cols = [
    'currency_id',
    'currency_code',
    'currency_name'
]

dim_counterparty_cols = [
    'counterparty_id',
    'counterparty_legal_name',
    'counterparty_legal_address_line_1',
    'counterparty_legal_address_line_2',
    'counterparty_legal_district',
    'counterparty_legal_city',
    'counterparty_legal_postal_code',
    'counterparty_legal_country',
    'counterparty_legal_phone_number'
]

payment_cols = [
    'payment_id', 'created_at', 'last_updated', 'transaction_id', 
    'counterparty_id', 'payment_amount', 'currency_id', 'payment_type_id', 
    'paid', 'payment_date', 'company_ac_number', 'counterparty_ac_number'
]
transaction_cols = [
    'transaction_id', 'transaction_type', 'sales_order_id', 
    'purchase_order_id', 'created_at', 'last_updated'
]
sales_order_cols = [
    'sales_order_id', 'created_at', 'last_updated', 'design_id', 'staff_id', 
    'counterparty_id', 'units_sold', 'unit_price', 'currency_id', 
    'agreed_delivery_date', 'agreed_payment_date', 
    'agreed_delivery_location_id'
]
purchase_order_cols = [
    'purchase_order_id', 'created_at', 'last_updated', 'staff_id', 
    'counterparty_id', 'item_code', 'item_quantity', 'item_unit_price', 
    'currency_id', 'agreed_delivery_date', 'agreed_payment_date', 
    'agreed_delivery_location_id'
]
counterparty_cols = [
    'counterparty_id', 'counterparty_legal_name', 'legal_address_id', 
    'commercial_contact', 'delivery_contact', 'created_at', 'last_updated'
]
address_cols = [
    'address_id', 'address_line_1', 'address_line_2', 'district', 'city', 
    'postal_code', 'country', 'phone', 'created_at', 'last_updated'
]
staff_cols = [
    'staff_id', 'first_name', 'last_name', 'department_id', 'email_address', 
    'created_at', 'last_updated'
]
department_cols = [
    'department_id', 'department_name', 'location', 'manager', 'created_at', 
    'last_updated'
]
currency_cols = [
    'currency_id', 'currency_code', 'created_at', 'last_updated'
]
design_cols = [
    'design_id', 'created_at', 'design_name', 'file_location', 'file_name', 
    'last_updated'
]
payment_type_cols = [
    'payment_type_id', 'payment_type_name', 'created_at', 'last_updated'
]

payment_first_row = [
    1, datetime(2022, 11, 3, 14, 20, 52, 187000), 
    datetime(2022, 11, 3, 14, 20, 52, 187000), 2, 5, Decimal('552548.62'), 
    2, 3, False, date(2022, 11, 4), 67305075, 31622269
]
transaction_first_row = [
    1, 'PURCHASE', None, 2, datetime(2022, 11, 3, 14, 20, 52, 186000), 
    datetime(2022, 11, 3, 14, 20, 52, 186000)
]
sales_order_first_row = [
    1, datetime(2022, 11, 3, 14, 20, 52, 186000), 
    datetime(2022, 11, 3, 14, 20, 52, 186000), 4, 7, 8, 203, 
    Decimal('4.55'), 2, date(2022, 11, 7), date(2022, 11, 8), 9
]
purchase_order_first_row = [
    1, datetime(2022, 11, 3, 14, 20, 52, 187000), 
    datetime(2022, 11, 3, 14, 20, 52, 187000), 2, 1, 'ZDOI5EA', 371, 
    Decimal('361.39'), 2, date(2022, 11, 9), date(2022, 11, 7), 6
]
counterparty_first_row = [
    1, 'Fahey and Sons', 5, 'Micheal Toy', 'Mrs. Lucy Runolfsdottir',
    datetime(2022, 11, 3, 14, 20, 51, 563000), 
    datetime(2022, 11, 3, 14, 20, 51, 563000)
]
address_first_row = [
    1, '6826 Herzog Via', None, 'Avon', 'New Patienceburgh', '28441', 
    'Turkey', '1803 637401', datetime(2022, 11, 3, 14, 20, 49, 962000), 
    datetime(2022, 11, 3, 14, 20, 49, 962000)
]
staff_first_row = [
    1, 'Jeremie', 'Franey', 2, 'jeremie.franey@terrifictotes.com', 
    datetime(2022, 11, 3, 14, 20, 51, 563000), 
    datetime(2022, 11, 3, 14, 20, 51, 563000)
]
department_first_row = [
    1, 'Sales', 'Manchester', 'Richard Roma', 
    datetime(2022, 11, 3, 14, 20, 49, 962000), 
    datetime(2022, 11, 3, 14, 20, 49, 962000)
]
currency_first_row = [
    1, 'GBP', datetime(2022, 11, 3, 14, 20, 49, 962000), 
    datetime(2022, 11, 3, 14, 20, 49, 962000)
]
design_first_row = [
    1, datetime(2022, 11, 3, 14, 20, 49, 962000), 
    datetime(2022, 11, 3, 14, 20, 49, 962000), 'Wooden', '/usr', 
    'wooden-20220717-npgz.json'
]
payment_type_first_row = [
    1, 'SALES_RECEIPT', datetime(2022, 11, 3, 14, 20, 49, 962000), 
    datetime(2022, 11, 3, 14, 20, 49, 962000)
]


warehouse_columns = [
    ('fact_sales_order', fact_sales_order_cols),
    ('dim_staff', dim_staff_cols),
    ('dim_location', dim_location_cols),
    ('dim_design', dim_design_cols),
    ('dim_date', dim_date_cols),
    ('dim_currency', dim_currency_cols),
    ('dim_counterparty', dim_counterparty_cols)
]

oltp_columns = [
    ('payment', payment_cols),
    ('transaction',transaction_cols),
    ('sales_order',sales_order_cols),
    ('purchase_order',purchase_order_cols),
    ('counterparty',counterparty_cols),
    ('address',address_cols),
    ('staff', staff_cols),
    ('department',department_cols),
    ('currency',currency_cols),
    ('design',design_cols),
    ('payment_type',payment_type_cols)
]

oltp_table_lengths = [
    ('payment', 10),
    ('transaction',45),
    ('sales_order',50),
    ('purchase_order',44),
    ('counterparty',10),
    ('address',10),
    ('staff', 10),
    ('department',8),
    ('currency',3),
    ('design',10),
    ('payment_type',4)
]

oltp_first_rows = [
    ('payment', payment_first_row),
    ('transaction',transaction_first_row),
    ('sales_order',sales_order_first_row),
    ('purchase_order',purchase_order_first_row),
    ('counterparty',counterparty_first_row),
    ('address',address_first_row),
    ('staff', staff_first_row),
    ('department',department_first_row),
    ('currency',currency_first_row),
    ('design',design_first_row),
    ('payment_type',payment_type_first_row)
]

