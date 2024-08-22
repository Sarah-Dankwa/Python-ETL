fact_sales_order_cols = [
        "sales_record_id",
        "sales_order_id",
        "created_date",
        "created_time",
        "last_updated_date",
        "last_updated_time",
        "sales_staff_id",
        "counterparty_id",
        "units_sold",
        "unit_price",
        "currency_id",
        "design_id",
        "agreed_payment_date",
        "agreed_delivery_date",
        "agreed_delivery_location_id"
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

oltp_testdata = []