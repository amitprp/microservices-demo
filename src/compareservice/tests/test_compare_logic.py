import os
import sys

import pytest

CURRENT_DIR = os.path.dirname(__file__)
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
sys.path.insert(0, PARENT_DIR)

from compare_logic import validate_product_ids, format_money, build_summary, extract_features, build_feature_matrix


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


# ============================================================================
# Tests for extract_features()
# ============================================================================


def test_extract_features_single_match():
    result = extract_features("This is a recycled product", ["recycled", "vintage"])
    assert result == {"recycled": True, "vintage": False}


def test_extract_features_multiple_matches():
    result = extract_features(
        "Recycled and durable item", ["recycled", "durable", "vintage"]
    )
    assert result == {"recycled": True, "durable": True, "vintage": False}


def test_extract_features_no_matches():
    result = extract_features("Just a regular product", ["recycled", "vintage"])
    assert result == {"recycled": False, "vintage": False}


def test_extract_features_case_insensitive():
    result = extract_features("RECYCLED materials", ["recycled"])
    assert result == {"recycled": True}


def test_extract_features_word_boundary():
    result = extract_features("unrecycled materials", ["recycled"])
    assert result == {"recycled": False}


def test_extract_features_empty_description():
    result = extract_features("", ["recycled"])
    assert result == {"recycled": False}


# ============================================================================
# Tests for build_feature_matrix()
# ============================================================================


def test_build_feature_matrix_basic():
    products = [
        {"id": "p1", "description": "A recycled product"},
        {"id": "p2", "description": "A durable product"},
    ]
    result = build_feature_matrix(products, keywords=["recycled", "durable", "vintage"])
    assert result["features"] == ["durable", "recycled"]
    assert result["matrix"]["p1"] == {"recycled": True, "durable": False}
    assert result["matrix"]["p2"] == {"recycled": False, "durable": True}


def test_build_feature_matrix_filters_unused_features():
    products = [
        {"id": "p1", "description": "A recycled product"},
        {"id": "p2", "description": "Another recycled item"},
    ]
    result = build_feature_matrix(products, keywords=["recycled", "vintage"])
    assert "vintage" not in result["features"]
    assert result["features"] == ["recycled"]
    assert "vintage" not in result["matrix"]["p1"]
    assert "vintage" not in result["matrix"]["p2"]


def test_build_feature_matrix_empty_products():
    result = build_feature_matrix([], keywords=["recycled"])
    assert result == {"features": [], "matrix": {}}


def test_build_feature_matrix_no_features_found():
    products = [
        {"id": "id1", "description": "A regular product"},
        {"id": "id2", "description": "Another normal item"},
    ]
    result = build_feature_matrix(products, keywords=["recycled", "vintage"])
    assert result["features"] == []
    assert result["matrix"]["id1"] == {}
    assert result["matrix"]["id2"] == {}


def test_build_feature_matrix_sorted_features():
    products = [
        {"id": "p1", "description": "durable and recycled and authentic product"},
    ]
    result = build_feature_matrix(
        products, keywords=["durable", "authentic", "recycled"]
    )
    assert result["features"] == ["authentic", "durable", "recycled"]
