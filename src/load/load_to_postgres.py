"""
Load stage: read the raw product JSON, generate reproducible synthetic
orders/order_items on top of it (since the public API has no transactional
data), and upsert everything into the `raw` schema in Postgres.

Synthetic data generation is seeded (RANDOM_SEED) so pipeline runs are
reproducible for testing and demos.
"""
import json
import os
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

from faker import Faker

from src.utils.db import get_connection
from src.utils.logger import get_logger

logger = get_logger(__name__)

DATA_DIR = Path(os.environ.get("RAW_DATA_DIR", "data/raw"))
ORDER_COUNT = int(os.environ.get("SYNTHETIC_ORDER_COUNT", "500"))
SEED = int(os.environ.get("RANDOM_SEED", "42"))
STATUSES = ["completed", "completed", "completed", "pending", "cancelled"]


def load_raw_products(path: Path = DATA_DIR / "products_latest.json") -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found — run src/extract/extract_api.py first."
        )
    return json.loads(path.read_text())


def upsert_products(cur, products: list[dict]) -> None:
    for p in products:
        rating = p.get("rating", {}) or {}
        cur.execute(
            """
            INSERT INTO raw.products
                (product_id, title, price, category, description, rating_rate, rating_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (product_id) DO UPDATE SET
                title = EXCLUDED.title,
                price = EXCLUDED.price,
                category = EXCLUDED.category,
                description = EXCLUDED.description,
                rating_rate = EXCLUDED.rating_rate,
                rating_count = EXCLUDED.rating_count,
                loaded_at = now();
            """,
            (
                p["id"],
                p["title"],
                p["price"],
                p["category"],
                p.get("description"),
                rating.get("rate"),
                rating.get("count"),
            ),
        )
    logger.info("Upserted %d products", len(products))


def generate_and_load_orders(cur, product_ids: list[int]) -> None:
    fake = Faker()
    Faker.seed(SEED)
    random.seed(SEED)

    today = datetime.now(tz=timezone.utc).date()
    order_id = 1
    for _ in range(ORDER_COUNT):
        customer_id = random.randint(1000, 1999)
        order_date = today - timedelta(days=random.randint(0, 365))
        status = random.choice(STATUSES)

        cur.execute(
            """
            INSERT INTO raw.orders (order_id, customer_id, order_date, status)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (order_id) DO NOTHING;
            """,
            (order_id, customer_id, order_date, status),
        )

        # 1-4 line items per order
        for _ in range(random.randint(1, 4)):
            product_id = random.choice(product_ids)
            quantity = random.randint(1, 3)
            cur.execute(
                """
                SELECT price FROM raw.products WHERE product_id = %s;
                """,
                (product_id,),
            )
            unit_price = cur.fetchone()[0]
            cur.execute(
                """
                INSERT INTO raw.order_items (order_id, product_id, quantity, unit_price)
                VALUES (%s, %s, %s, %s);
                """,
                (order_id, product_id, quantity, unit_price),
            )
        order_id += 1

    logger.info("Generated and loaded %d synthetic orders", ORDER_COUNT)
    _ = fake  # fake reserved for future use (customer names, etc.)


def run() -> None:
    products = load_raw_products()
    product_ids = [p["id"] for p in products]

    conn = get_connection()
    try:
        with conn,conn.cursor() as cur:
                # Clear transactional tables for idempotent re-runs; products upsert instead.
                cur.execute("TRUNCATE raw.order_items, raw.orders RESTART IDENTITY CASCADE;")
                upsert_products(cur, products)
                generate_and_load_orders(cur, product_ids)
        logger.info("Load complete.")
    finally:
        conn.close()


if __name__ == "__main__":
    run()
