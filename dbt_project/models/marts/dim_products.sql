select
    product_id,
    product_title,
    category,
    unit_price,
    rating_rate,
    rating_count
from {{ ref('stg_products') }}
