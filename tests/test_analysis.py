from pathlib import Path

import pandas as pd
import pytest

from analysis.data import load_data
from analysis.metrics import cohort_retention, summarize


@pytest.fixture
def retail_data(tmp_path):
    tables = {
        "customers": pd.DataFrame({"customer_id": ["C1", "C2"], "country": ["Germany", "France"]}),
        "products": pd.DataFrame({"product_id": ["P1", "P2"], "product_name": ["Lamp", "Mug"], "category": ["Home", "Kitchen"]}),
        "orders": pd.DataFrame([
            ["O1", "C1", "2025-01-01", "Email", "delivered"],
            ["O2", "C1", "2025-02-01", "Email", "returned"],
            ["O3", "C2", "2025-03-01", "Organic", "cancelled"],
            ["O4", "C1", "2025-02-02", "Email", "delivered"],
        ], columns=["order_id", "customer_id", "order_date", "channel", "status"]),
        "order_items": pd.DataFrame([
            ["O1", "P1", 2, 50, 20, .1], ["O1", "P2", 1, 20, 10, 0],
            ["O2", "P1", 1, 50, 20, 0], ["O3", "P2", 1, 20, 10, 0],
            ["O4", "P2", 1, 20, 10, 0],
        ], columns=["order_id", "product_id", "quantity", "unit_price", "unit_cost", "discount_rate"]),
    }
    for name, frame in tables.items():
        frame.to_csv(tmp_path / f"{name}.csv", index=False)
    return tmp_path


def test_revenue_order_grain_and_return_denominator(retail_data):
    lines, _ = load_data(retail_data)
    result = summarize(lines)
    assert result["revenue"] == 130
    assert result["profit"] == 70
    assert result["orders"] == 2
    assert result["aov"] == 65
    assert result["return_rate"] == pytest.approx(1 / 3)
    assert result["refunds"] == 50
    assert result["repeat_rate"] == 1


def test_duplicate_dimension_keys_rejected_before_join(retail_data):
    file = retail_data / "products.csv"
    products = pd.read_csv(file)
    pd.concat([products, products.iloc[:1]]).to_csv(file, index=False)
    with pytest.raises(ValueError, match="duplicate product_id"):
        load_data(retail_data)


def test_unknown_product_rejected(retail_data):
    file = retail_data / "order_items.csv"
    items = pd.read_csv(file)
    items.loc[0, "product_id"] = "UNKNOWN"
    items.to_csv(file, index=False)
    with pytest.raises(ValueError, match="unknown product_id"):
        load_data(retail_data)


def test_invalid_discount_rejected(retail_data):
    file = retail_data / "order_items.csv"
    items = pd.read_csv(file)
    items.loc[0, "discount_rate"] = 1.5
    items.to_csv(file, index=False)
    with pytest.raises(ValueError, match="invalid quantity"):
        load_data(retail_data)


def test_cohort_zero_month_and_future_month_are_different():
    frame = pd.DataFrame({"customer_id": ["A", "A", "B"],
                          "order_date": pd.to_datetime(["2025-01-01", "2025-03-01", "2025-02-01"]),
                          "status": ["delivered"] * 3})
    result = cohort_retention(frame)
    assert result.loc["2025-01", 1] == 0
    assert result.loc["2025-01", 2] == 1
    assert pd.isna(result.loc["2025-02", 2])


def test_no_delivered_orders_has_no_undefined_metrics(retail_data):
    lines, _ = load_data(retail_data)
    result = summarize(lines[lines.status.eq("cancelled")])
    assert all(value == 0 for value in result.values())


def test_bundled_data_passes_relational_checks():
    lines, _ = load_data()
    assert len(lines) == len(pd.read_csv(Path(__file__).resolve().parents[1] / "data/order_items.csv"))
    assert lines.revenue.ge(0).all()
