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


def build_product(product_id, name, units, nanos=0, description=None):
    if description is None:
        description = f"{name} description"
    return demo_pb2.Product(
        id=product_id,
        name=name,
        description=description,
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

    def test_compare_response_includes_feature_matrix(self):
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

    def test_compare_feature_matrix_structure(self):
        products_by_id = {
            "sku-1": build_product(
                "sku-1", "Alpha", units=10, description="A recycled product"
            ),
            "sku-2": build_product(
                "sku-2", "Beta", units=5, description="A durable item"
            ),
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
        feature_matrix = payload["feature_matrix"]
        self.assertIn("features", feature_matrix)
        self.assertIn("matrix", feature_matrix)
        self.assertIsInstance(feature_matrix["features"], list)
        self.assertIsInstance(feature_matrix["matrix"], dict)

    def test_compare_feature_matrix_matches_products(self):
        products_by_id = {
            "sku-1": build_product(
                "sku-1", "Alpha", units=10, description="A recycled product"
            ),
            "sku-2": build_product(
                "sku-2", "Beta", units=5, description="A durable item"
            ),
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
        product_ids = [p["id"] for p in payload["products"]]
        matrix_keys = list(payload["feature_matrix"]["matrix"].keys())
        self.assertEqual(sorted(product_ids), sorted(matrix_keys))


if __name__ == "__main__":
    unittest.main()
