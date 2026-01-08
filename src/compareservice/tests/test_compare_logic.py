import os
import sys

import pytest

CURRENT_DIR = os.path.dirname(__file__)
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
sys.path.insert(0, PARENT_DIR)

from compare_logic import validate_product_ids, format_money, build_summary, build_feature_matrix


def test_validate_product_ids_two_ok():
    assert validate_product_ids(["id1", "id2"]) == ["id1", "id2"]


def test_validate_product_ids_three_ok():
    assert validate_product_ids(["id1", "id2", "id3"]) == ["id1", "id2", "id3"]


def test_validate_product_ids_one_error():
    with pytest.raises(ValueError, match="At least 2 products required"):
        validate_product_ids(["id1"])


def test_validate_product_ids_four_error():
    with pytest.raises(ValueError, match="Maximum 3 products allowed"):
        validate_product_ids(["id1", "id2", "id3", "id4"])


def test_validate_product_ids_non_list_error():
    with pytest.raises(ValueError, match="product_ids must be a list"):
        validate_product_ids("id1")


def test_validate_product_ids_duplicates_allowed():
    assert validate_product_ids(["id1", "id1"]) == ["id1", "id1"]


def test_format_money_units_and_nanos():
    assert format_money({"units": 12, "nanos": 340000000}) == "$12.34"


def test_build_summary_picks_cheapest_and_formats_price():
    products = [
        {"name": "A", "price": {"units": 10, "nanos": 0}},
        {"name": "B", "price": {"units": 9, "nanos": 500000000}},
        {"name": "C", "price": {"units": 11, "nanos": 250000000}},
    ]
    assert build_summary(products) == "B is the cheapest option at $9.50"


def test_build_summary_empty_products():
    assert build_summary([]) == ""


def test_build_summary_single_product():
    products = [{"name": "Solo", "price": {"units": 5, "nanos": 0}}]
    assert build_summary(products) == "Solo is the cheapest option at $5.00"


def test_format_money_zero_price():
    assert format_money({"units": 0, "nanos": 0}) == "$0.00"


def test_format_money_missing_fields():
    assert format_money({}) == "$0.00"


def test_format_money_only_nanos():
    assert format_money({"nanos": 990000000}) == "$0.99"


def test_validate_product_ids_empty_list():
    with pytest.raises(ValueError, match="At least 2 products required"):
        validate_product_ids([])


def test_build_feature_matrix_basic():
    products = [
        {"id": "p1", "categories": ["clothing", "outdoor"]},
        {"id": "p2", "categories": ["outdoor", "accessories"]},
    ]
    result = build_feature_matrix(products)
    assert "accessories" in result["features"]
    assert "clothing" in result["features"]
    assert "outdoor" in result["features"]
    assert result["matrix"]["p1"]["clothing"] is True
    assert result["matrix"]["p1"]["accessories"] is False
    assert result["matrix"]["p2"]["outdoor"] is True


def test_build_feature_matrix_empty_products():
    result = build_feature_matrix([])
    assert result == {"features": [], "matrix": {}}


def test_build_feature_matrix_no_categories():
    products = [
        {"id": "p1", "categories": []},
        {"id": "p2", "categories": []},
    ]
    result = build_feature_matrix(products)
    assert result["features"] == []


def test_build_feature_matrix_sorted_features():
    products = [
        {"id": "p1", "categories": ["zebra", "apple", "mango"]},
    ]
    result = build_feature_matrix(products)
    assert result["features"] == ["apple", "mango", "zebra"]


def test_build_feature_matrix_single_product():
    products = [{"id": "solo", "categories": ["tech"]}]
    result = build_feature_matrix(products)
    assert result["features"] == ["tech"]
    assert result["matrix"]["solo"]["tech"] is True
