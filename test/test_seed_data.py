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

warehouse_testdata = [
    ('fact_sales_order', fact_sales_order_cols),
    ('dim_staff', dim_staff_cols),
    ('dim_location', dim_location_cols),
    ('dim_design', dim_design_cols),
    ('dim_date', dim_date_cols),
    ('dim_currency', dim_currency_cols),
    ('dim_counterparty', dim_counterparty_cols)
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

oltp_testdata = [
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