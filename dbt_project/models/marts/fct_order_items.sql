-- Primary analytics-grain fact table: one row per order line item,
-- pre-joined to product and order attributes for easy slicing.

select
    oi.order_item_id,
    oi.order_id,
    o.order_date,
    o.order_status,
    o.customer_id,
    oi.product_id,
    p.product_title,
    p.category,
    oi.quantity,
    oi.unit_price,
    oi.line_amount
from {{ ref('stg_order_items') }} oi
join {{ ref('stg_orders') }} o    on oi.order_id = o.order_id
join {{ ref('stg_products') }} p on oi.product_id = p.product_id
