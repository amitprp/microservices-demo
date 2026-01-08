import os
import sys
from pathlib import Path
import unittest
from unittest import mock

os.environ.setdefault("PRODUCT_CATALOG_SERVICE_ADDR", "test")

TESTS_DIR = Path(__file__).resolve().parent
SERVICE_DIR = TESTS_DIR.parent
sys.path.append(str(SERVICE_DIR))

import compareservice
import demo_pb2


def build_product(product_id, name, units, nanos=0):
    return demo_pb2.Product(
        id=product_id,
        name=name,
        description=f"{name} description",
        picture=f"{product_id}.png",
        price_usd=demo_pb2.Money(currency_code="USD", units=units, nanos=nanos),
        categories=["cat"],
    )


class CompareServiceIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.app = compareservice.create_app()
        self.client = self.app.test_client()

    def test_compare_products_success(self):
        products_by_id = {
            "sku-1": build_product("sku-1", "Alpha", units=10),
            "sku-2": build_product("sku-2", "Beta", units=5),
        }

        def fake_get_product(request):
            return products_by_id[request.id]

        with mock.patch.object(
            compareservice.product_catalog_stub, "GetProduct", side_effect=fake_get_product
        ):
            response = self.client.post(
                "/compare", json={"product_ids": ["sku-1", "sku-2"]}
            )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(len(payload["products"]), 2)
        self.assertEqual(payload["products"][0]["id"], "sku-1")
        self.assertEqual(payload["products"][1]["id"], "sku-2")
        self.assertEqual(
            payload["summary"], "Beta is the cheapest option at $5.00"
        )

    def test_compare_products_missing_ids(self):
        response = self.client.post("/compare", json={})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "product_ids required")

    def test_compare_returns_feature_matrix(self):
        products_by_id = {
            "sku-1": build_product("sku-1", "Alpha", units=10),
            "sku-2": build_product("sku-2", "Beta", units=5),
        }

        def fake_get_product(request):
            return products_by_id[request.id]

        with mock.patch.object(
            compareservice.product_catalog_stub, "GetProduct", side_effect=fake_get_product
        ):
            response = self.client.post(
                "/compare", json={"product_ids": ["sku-1", "sku-2"]}
            )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("feature_matrix", payload)
        self.assertIn("features", payload["feature_matrix"])
        self.assertIn("matrix", payload["feature_matrix"])

    def test_compare_validates_too_few_products(self):
        response = self.client.post("/compare", json={"product_ids": ["only-one"]})

        self.assertEqual(response.status_code, 400)
        self.assertIn("At least 2", response.get_json()["error"])

    def test_compare_validates_too_many_products(self):
        response = self.client.post(
            "/compare", json={"product_ids": ["a", "b", "c", "d"]}
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Maximum 3", response.get_json()["error"])


if __name__ == "__main__":
    unittest.main()
