select
    order_item_id,
    order_id,
    product_id,
    quantity,
    unit_price::numeric(10, 2)              as unit_price,
    (quantity * unit_price)::numeric(10, 2)  as line_amount,
    loaded_at
from {{ source('raw', 'order_items') }}
