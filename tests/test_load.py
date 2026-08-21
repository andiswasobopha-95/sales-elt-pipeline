import json

import pytest

from src.load.load_to_postgres import load_raw_products


def test_load_raw_products_reads_json(tmp_path):
    sample = [{"id": 1, "title": "Widget", "price": 9.99}]
    path = tmp_path / "products_latest.json"
    path.write_text(json.dumps(sample))

    result = load_raw_products(path=path)

    assert result == sample


def test_load_raw_products_missing_file_raises(tmp_path):
    missing = tmp_path / "does_not_exist.json"

    with pytest.raises(FileNotFoundError):
        load_raw_products(path=missing)
