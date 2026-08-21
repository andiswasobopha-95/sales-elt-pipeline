"""
Extract stage: pull the product catalog from the public Fake Store API
and land it as raw JSON on disk. This is the only network call in the
pipeline, isolated from the load/transform stages so it can be retried,
mocked in tests, and cached independently.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests

from src.utils.logger import get_logger

logger = get_logger(__name__)

API_URL = os.environ.get("FAKE_STORE_API_URL", "https://fakestoreapi.com/products")
DATA_DIR = Path(os.environ.get("RAW_DATA_DIR", "data/raw"))


def fetch_products(api_url: str = API_URL, timeout: int = 15) -> list[dict]:
    """Fetch the product catalog. Raises on HTTP/network errors."""
    logger.info("Fetching products from %s", api_url)
    response = requests.get(api_url, timeout=timeout)
    response.raise_for_status()
    products = response.json()
    logger.info("Fetched %d products", len(products))
    return products


def save_raw(products: list[dict], data_dir: Path = DATA_DIR) -> Path:
    """Persist raw API response to disk, timestamped for lineage/debugging."""
    data_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = data_dir / f"products_{ts}.json"
    out_path.write_text(json.dumps(products, indent=2))

    # Also write a stable "latest" copy that downstream steps read from
    latest_path = data_dir / "products_latest.json"
    latest_path.write_text(json.dumps(products, indent=2))

    logger.info("Saved raw products to %s and %s", out_path, latest_path)
    return latest_path


def run() -> Path:
    products = fetch_products()
    return save_raw(products)


if __name__ == "__main__":
    run()
