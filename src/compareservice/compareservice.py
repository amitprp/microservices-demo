#!/usr/bin/python
#
# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import grpc
from flask import Flask, request, jsonify, send_file

import demo_pb2
import demo_pb2_grpc

from logger import getJSONLogger
from compare_logic import validate_product_ids, build_summary

logger = getJSONLogger('compareservice')

# Get product catalog service address from environment
catalog_addr = os.environ.get('PRODUCT_CATALOG_SERVICE_ADDR', '')
if catalog_addr == "":
    raise Exception('PRODUCT_CATALOG_SERVICE_ADDR environment variable not set')

logger.info(f"product catalog address: {catalog_addr}")
channel = grpc.insecure_channel(catalog_addr)
product_catalog_stub = demo_pb2_grpc.ProductCatalogServiceStub(channel)


def create_app():
    app = Flask(__name__)

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({"status": "healthy"}), 200

    @app.route('/openapi.yaml', methods=['GET'])
    def openapi_spec():
        spec_path = os.path.join(os.path.dirname(__file__), 'openapi.yaml')
        return send_file(spec_path, mimetype='application/yaml')

    @app.route('/compare', methods=['POST'])
    def compare_products():
        """
        Compare 2-3 products.
        Request body: { "product_ids": ["id1", "id2", "id3"] }
        Response: { "products": [...], "summary": "..." }
        """
        data = request.get_json()

        if not data or 'product_ids' not in data:
            return jsonify({"error": "product_ids required"}), 400

        product_ids = data['product_ids']
        try:
            validate_product_ids(product_ids)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        logger.info(f"[CompareProducts] comparing products: {product_ids}")

        # Fetch product details from ProductCatalogService
        products = []
        for product_id in product_ids:
            try:
                product = product_catalog_stub.GetProduct(
                    demo_pb2.GetProductRequest(id=product_id)
                )

                product_data = {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "picture": product.picture,
                    "price": {
                        "currency_code": product.price_usd.currency_code,
                        "units": product.price_usd.units,
                        "nanos": product.price_usd.nanos
                    },
                    "categories": list(product.categories)
                }
                products.append(product_data)

            except grpc.RpcError as e:
                logger.error(f"Failed to get product {product_id}: {e}")
                return jsonify({"error": f"Product not found: {product_id}"}), 404

        # Generate summary
        summary = build_summary(products)

        logger.info(f"[CompareProducts] returning {len(products)} products")

        return jsonify({
            "products": products,
            "summary": summary
        })

    return app


if __name__ == "__main__":
    app = create_app()
    port = os.environ.get('PORT', '8080')
    logger.info(f"Starting compareservice on port {port}")
    app.run(host='0.0.0.0', port=int(port))
