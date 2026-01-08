import os
import sys

import pytest

CURRENT_DIR = os.path.dirname(__file__)
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
sys.path.insert(0, PARENT_DIR)

from compare_logic import validate_product_ids, format_money, build_summary


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
