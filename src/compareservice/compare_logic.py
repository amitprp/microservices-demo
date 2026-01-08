import re

FEATURE_KEYWORDS = [
    "recycled", "organic", "sustainable", "eco-friendly",
    "durable", "premium", "handmade", "authentic",
    "lightweight", "portable", "compact", "vintage",
    "classic", "modern", "stylish", "minimalist"
]


def validate_product_ids(ids):
    if not isinstance(ids, list):
        raise ValueError("product_ids must be a list")
    if len(ids) < 2:
        raise ValueError("At least 2 products required for comparison")
    if len(ids) > 3:
        raise ValueError("Maximum 3 products allowed for comparison")
    return ids


def format_money(price):
    units = price.get("units", 0)
    nanos = price.get("nanos", 0)
    cents = nanos // 10_000_000
    return f"${units}.{cents:02d}"


def build_summary(products):
    if not products:
        return ""

    def total_price_nanos(product):
        price = product.get("price", {})
        units = price.get("units", 0)
        nanos = price.get("nanos", 0)
        return units * 1_000_000_000 + nanos

    cheapest = min(products, key=total_price_nanos)
    price_str = format_money(cheapest.get("price", {}))
    return f"{cheapest.get('name')} is the cheapest option at {price_str}"


def extract_features(description, keywords):
    """
    Scan description text for presence of each keyword.
    Uses word-boundary matching (case-insensitive).
    Returns dict mapping keyword -> True/False
    """
    result = {}
    description_lower = description.lower()
    for keyword in keywords:
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        result[keyword] = bool(re.search(pattern, description_lower))
    return result


def build_feature_matrix(products, keywords=None):
    """
    For each product, extract features from description.
    Returns:
    {
        "features": [list of features found in ANY product, sorted],
        "matrix": {
            product_id: {feature: bool, ...},
            ...
        }
    }
    Only includes features that appear in at least one product.
    """
    if keywords is None:
        keywords = FEATURE_KEYWORDS

    matrix = {}
    found_features = set()

    for product in products:
        product_id = product.get("id", "")
        description = product.get("description", "")
        features = extract_features(description, keywords)
        matrix[product_id] = features

        for keyword, present in features.items():
            if present:
                found_features.add(keyword)

    # Filter matrix to only include found features
    filtered_matrix = {}
    for product_id, features in matrix.items():
        filtered_matrix[product_id] = {
            k: v for k, v in features.items() if k in found_features
        }

    return {
        "features": sorted(list(found_features)),
        "matrix": filtered_matrix
    }
