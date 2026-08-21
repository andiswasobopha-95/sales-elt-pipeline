-- 1:1 cleaned view over raw.products: rename, cast, no business logic.

select
    product_id,
    trim(title)            as product_title,
    price::numeric(10, 2)  as unit_price,
    lower(trim(category))  as category,
    rating_rate             as rating_rate,
    coalesce(rating_count, 0) as rating_count,
    loaded_at
from {{ source('raw', 'products') }}
