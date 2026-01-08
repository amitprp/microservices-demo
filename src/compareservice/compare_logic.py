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
