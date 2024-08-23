"""test data for the transaction table in the oltp database"""

transaction = [
    {
        'transaction_id': 1,
        'transaction_type': 'PURCHASE',
        'sales_order_id': None,
        'purchase_order_id': 2,
        'created_at': '2022-11-03 14:20:52.186000',
        'last_updated': '2022-11-03 14:20:52.186000'
    },
    {
        'transaction_id': 2,
        'transaction_type': 'PURCHASE',
        'sales_order_id': None,
        'purchase_order_id': 3,
        'created_at': '2022-11-03 14:20:52.187000',
        'last_updated': '2022-11-03 14:20:52.187000'
    },
    {
        'transaction_id': 3,
        'transaction_type': 'SALE',
        'sales_order_id': 1,
        'purchase_order_id': None,
        'created_at': '2022-11-03 14:20:52.186000',
        'last_updated': '2022-11-03 14:20:52.186000'
    },
    {
        'transaction_id': 4,
        'transaction_type': 'PURCHASE',
        'sales_order_id': None,
        'purchase_order_id': 1,
        'created_at': '2022-11-03 14:20:52.187000',
        'last_updated': '2022-11-03 14:20:52.187000'
    },
    {
        'transaction_id': 5,
        'transaction_type': 'PURCHASE',
        'sales_order_id': None,
        'purchase_order_id': 4,
        'created_at': '2022-11-03 14:20:52.187000',
        'last_updated': '2022-11-03 14:20:52.187000'
    },
    {
        'transaction_id': 6,
        'transaction_type': 'SALE',
        'sales_order_id': 2,
        'purchase_order_id': None,
        'created_at': '2022-11-03 14:20:52.186000',
        'last_updated': '2022-11-03 14:20:52.186000'
    },
    {
        'transaction_id': 7,
        'transaction_type': 'SALE',
        'sales_order_id': 3,
        'purchase_order_id': None,
        'created_at': '2022-11-03 14:20:52.188000',
        'last_updated': '2022-11-03 14:20:52.188000'
    },
    {
        'transaction_id': 8,
        'transaction_type': 'PURCHASE',
        'sales_order_id': None,
        'purchase_order_id': 5,
        'created_at': '2022-11-03 14:20:52.186000',
        'last_updated': '2022-11-03 14:20:52.186000'
    },
    {
        'transaction_id': 9,
        'transaction_type': 'SALE',
        'sales_order_id': 5,
        'purchase_order_id': None,
        'created_at': '2022-11-03 14:20:52.186000',
        'last_updated': '2022-11-03 14:20:52.186000'
    },
    {
        'transaction_id': 10,
        'transaction_type': 'SALE',
        'sales_order_id': 4,
        'purchase_order_id': None,
        'created_at': '2022-11-03 14:20:52.188000',
        'last_updated': '2022-11-03 14:20:52.188000'
    },
    {
        'transaction_id': 11,
        'transaction_type': 'SALE',
        'sales_order_id': 6,
        'purchase_order_id': None,
        'created_at': '2022-11-04 11:37:10.341000',
        'last_updated': '2022-11-04 11:37:10.341000'
    },
    {
        'transaction_id': 12,
        'transaction_type': 'PURCHASE',
        'sales_order_id': None,
        'purchase_order_id': 6,
        'created_at': '2022-11-04 11:59:09.990000',
        'last_updated': '2022-11-04 11:59:09.990000'
    },
    {
        'transaction_id': 13,
        'transaction_type': 'PURCHASE',
        'sales_order_id': None,
        'purchase_order_id': 7,
        'created_at': '2022-11-04 12:18:09.885000',
        'last_updated': '2022-11-04 12:18:09.885000'
    },
    {
        'transaction_id': 14,
        'transaction_type': 'SALE',
        'sales_order_id': 7,
        'purchase_order_id': None,
        'created_at': '2022-11-04 12:57:09.926000',
        'last_updated': '2022-11-04 12:57:09.926000'
    },
    {
        'transaction_id': 15,
        'transaction_type': 'SALE',
        'sales_order_id': 8,
        'purchase_order_id': None,
        'created_at': '2022-11-04 13:45:10.306000',
        'last_updated': '2022-11-04 13:45:10.306000'
    },
    {
        'transaction_id': 16,
        'transaction_type': 'SALE',
        'sales_order_id': 9,
        'purchase_order_id': None,
        'created_at': '2022-11-04 15:42:10.886000',
        'last_updated': '2022-11-04 15:42:10.886000'
    },
    {
        'transaction_id': 17,
        'transaction_type': 'PURCHASE',
        'sales_order_id': None,
        'purchase_order_id': 8,
        'created_at': '2022-11-04 18:03:10.233000',
        'last_updated': '2022-11-04 18:03:10.233000'
    },
    {
        'transaction_id': 18,
        'transaction_type': 'SALE',
        'sales_order_id': 10,
        'purchase_order_id': None,
        'created_at': '2022-11-07 09:07:10.485000',
        'last_updated': '2022-11-07 09:07:10.485000'
    },
    {
        'transaction_id': 20,
        'transaction_type': 'SALE',
        'sales_order_id': 11,
        'purchase_order_id': None,
        'created_at': '2022-11-07 15:53:10.153000',
        'last_updated': '2022-11-07 15:53:10.153000'
    },
    {
        'transaction_id': 21,
        'transaction_type': 'PURCHASE',
        'sales_order_id': None,
        'purchase_order_id': 10,
        'created_at': '2022-11-07 17:06:10.294000',
        'last_updated': '2022-11-07 17:06:10.294000'
    },
    {
        'transaction_id': 22,
        'transaction_type': 'PURCHASE',
        'sales_order_id': None,
        'purchase_order_id': 11,
        'created_at': '2022-11-07 17:36:09.898000',
        'last_updated': '2022-11-07 17:36:09.898000'
    },
    {
        'transaction_id': 24,
        'transaction_type': 'PURCHASE',
        'sales_order_id': None,
        'purchase_order_id': 13,
        'created_at': '2022-11-08 15:30:10.600000',
        'last_updated': '2022-11-08 15:30:10.600000'
    },
    {
        'transaction_id': 25,
        'transaction_type': 'PURCHASE',
        'sales_order_id': None,
        'purchase_order_id': 14,
        'created_at': '2022-11-08 17:34:09.912000',
        'last_updated': '2022-11-08 17:34:09.912000'
    },
    {
        'transaction_id': 26,
        'transaction_type': 'PURCHASE',
        'sales_order_id': None,
        'purchase_order_id': 15,
        'created_at': '2022-11-08 18:50:10.306000',
        'last_updated': '2022-11-08 18:50:10.306000'
    },
    {
        'transaction_id': 27,
        'transaction_type': 'PURCHASE',
        'sales_order_id': None,
        'purchase_order_id': 16,
        'created_at': '2022-11-09 08:41:10.654000',
        'last_updated': '2022-11-09 08:41:10.654000'
    },
    {
        'transaction_id': 28,
        'transaction_type': 'SALE',
        'sales_order_id': 12,
        'purchase_order_id': None,
        'created_at': '2022-11-09 10:20:09.912000',
        'last_updated': '2022-11-09 10:20:09.912000'
    },
    {
        'transaction_id': 29,
        'transaction_type': 'SALE',
        'sales_order_id': 13,
        'purchase_order_id': None,
        'created_at': '2022-11-09 15:16:10.492000',
        'last_updated': '2022-11-09 15:16:10.492000'
    },
    {
        'transaction_id': 30,
        'transaction_type': 'PURCHASE',
        'sales_order_id': None,
        'purchase_order_id': 17,
        'created_at': '2022-11-10 13:10:10.329000',
        'last_updated': '2022-11-10 13:10:10.329000'
    },
    {
        'transaction_id': 31,
        'transaction_type': 'PURCHASE',
        'sales_order_id': None,
        'purchase_order_id': 18,
        'created_at': '2022-11-10 13:16:09.911000',
        'last_updated': '2022-11-10 13:16:09.911000'
    },
    {
        'transaction_id': 32,
        'transaction_type': 'SALE',
        'sales_order_id': 14,
        'purchase_order_id': None,
        'created_at': '2022-11-10 13:18:09.926000',
        'last_updated': '2022-11-10 13:18:09.926000'
    },
    {
        'transaction_id': 33,
        'transaction_type': 'PURCHASE',
        'sales_order_id': None,
        'purchase_order_id': 19,
        'created_at': '2022-11-10 15:49:10.108000',
        'last_updated': '2022-11-10 15:49:10.108000'
    },
    {
        'transaction_id': 34,
        'transaction_type': 'SALE',
        'sales_order_id': 15,
        'purchase_order_id': None,
        'created_at': '2022-11-11 08:51:10.286000',
        'last_updated': '2022-11-11 08:51:10.286000'
    },
    {
        'transaction_id': 35,
        'transaction_type': 'PURCHASE',
        'sales_order_id': None,
        'purchase_order_id': 20,
        'created_at': '2022-11-11 11:18:10.421000',
        'last_updated': '2022-11-11 11:18:10.421000'
    },
    {
        'transaction_id': 36,
        'transaction_type': 'PURCHASE',
        'sales_order_id': None,
        'purchase_order_id': 21,
        'created_at': '2022-11-11 14:25:10.197000',
        'last_updated': '2022-11-11 14:25:10.197000'
    },
    {
        'transaction_id': 37,
        'transaction_type': 'PURCHASE',
        'sales_order_id': None,
        'purchase_order_id': 22,
        'created_at': '2022-11-11 17:40:10.497000',
        'last_updated': '2022-11-11 17:40:10.497000'
    },
    {
        'transaction_id': 38,
        'transaction_type': 'PURCHASE',
        'sales_order_id': None,
        'purchase_order_id': 23,
        'created_at': '2022-11-14 08:12:10.313000',
        'last_updated': '2022-11-14 08:12:10.313000'
    },
    {
        'transaction_id': 39,
        'transaction_type': 'SALE',
        'sales_order_id': 16,
        'purchase_order_id': None,
        'created_at': '2022-11-14 15:32:10.333000',
        'last_updated': '2022-11-14 15:32:10.333000'
    },
    {
        'transaction_id': 40,
        'transaction_type': 'PURCHASE',
        'sales_order_id': None,
        'purchase_order_id': 24,
        'created_at': '2022-11-14 18:25:10.356000',
        'last_updated': '2022-11-14 18:25:10.356000'
    },
    {
        'transaction_id': 42,
        'transaction_type': 'SALE',
        'sales_order_id': 17,
        'purchase_order_id': None,
        'created_at': '2022-11-15 08:46:09.873000',
        'last_updated': '2022-11-15 08:46:09.873000'
    },
    {
        'transaction_id': 43,
        'transaction_type': 'PURCHASE',
        'sales_order_id': None,
        'purchase_order_id': 26,
        'created_at': '2022-11-15 08:46:09.877000',
        'last_updated': '2022-11-15 08:46:09.877000'
    },
    {
        'transaction_id': 44,
        'transaction_type': 'PURCHASE',
        'sales_order_id': None,
        'purchase_order_id': 27,
        'created_at': '2022-11-15 15:39:10.617000',
        'last_updated': '2022-11-15 15:39:10.617000'
    },
    {
        'transaction_id': 45,
        'transaction_type': 'PURCHASE',
        'sales_order_id': None,
        'purchase_order_id': 28,
        'created_at': '2022-11-15 17:12:10.531000',
        'last_updated': '2022-11-15 17:12:10.531000'
    },
    {
        'transaction_id': 46,
        'transaction_type': 'SALE',
        'sales_order_id': 18,
        'purchase_order_id': None,
        'created_at': '2022-11-16 08:17:10.016000',
        'last_updated': '2022-11-16 08:17:10.016000'
    },
    {
        'transaction_id': 47,
        'transaction_type': 'SALE',
        'sales_order_id': 19,
        'purchase_order_id': None,
        'created_at': '2022-11-16 09:05:10.336000',
        'last_updated': '2022-11-16 09:05:10.336000'
    },
    {
        'transaction_id': 49,
        'transaction_type': 'SALE',
        'sales_order_id': 21,
        'purchase_order_id': None,
        'created_at': '2022-11-17 11:47:09.942000',
        'last_updated': '2022-11-17 11:47:09.942000'
    }
]