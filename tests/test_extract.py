import json

from src.extract.extract_api import fetch_products, save_raw


class DummyResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


def test_fetch_products_returns_list(mocker):
    sample = [{"id": 1, "title": "Widget", "price": 9.99, "category": "misc"}]
    mocker.patch(
        "src.extract.extract_api.requests.get",
        return_value=DummyResponse(sample),
    )

    result = fetch_products(api_url="https://fake.test/products")

    assert result == sample


def test_save_raw_writes_json_files(tmp_path):
    sample = [{"id": 1, "title": "Widget", "price": 9.99}]

    out_path = save_raw(sample, data_dir=tmp_path)

    assert out_path.exists()
    latest = tmp_path / "products_latest.json"
    assert latest.exists()
    assert json.loads(latest.read_text()) == sample
