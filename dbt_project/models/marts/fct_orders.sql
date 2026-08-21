select
    o.order_id,
    o.customer_id,
    o.order_date,
    o.order_status,
    count(oi.order_item_id)      as item_count,
    sum(oi.line_amount)          as order_total
from {{ ref('stg_orders') }} o
left join {{ ref('stg_order_items') }} oi
    on o.order_id = oi.order_id
group by 1, 2, 3, 4
