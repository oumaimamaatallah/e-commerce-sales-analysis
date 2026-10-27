from pathlib import Path
import sqlite3

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def load_data(directory=None):
    """Validate relational keys before joining, so bad rows cannot multiply sales."""
    directory = Path(directory or ROOT / "data")
    tables = {name: pd.read_csv(directory / f"{name}.csv")
              for name in ["customers", "products", "orders", "order_items"]}
    required = {
        "customers": {"customer_id", "country"},
        "products": {"product_id", "product_name", "category"},
        "orders": {"order_id", "customer_id", "order_date", "channel", "status"},
        "order_items": {"order_id", "product_id", "quantity", "unit_price", "unit_cost", "discount_rate"},
    }
    for name, columns in required.items():
        missing = columns - set(tables[name].columns)
        if missing:
            raise ValueError(f"{name}: missing columns {', '.join(sorted(missing))}")
        if tables[name][list(columns)].isna().any().any():
            raise ValueError(f"{name}: required values cannot be blank")
        if tables[name].empty:
            raise ValueError(f"{name}: must contain at least one row")
    for table, key in [("customers", "customer_id"), ("products", "product_id"), ("orders", "order_id")]:
        if tables[table][key].duplicated().any():
            raise ValueError(f"{table}: duplicate {key}")
    items, orders = tables["order_items"], tables["orders"]
    if items.duplicated(["order_id", "product_id"]).any():
        raise ValueError("order_items: duplicate order/product pair")
    for child, fk, parent, pk in [
        ("orders", "customer_id", "customers", "customer_id"),
        ("order_items", "order_id", "orders", "order_id"),
        ("order_items", "product_id", "products", "product_id"),
    ]:
        if not tables[child][fk].isin(tables[parent][pk]).all():
            raise ValueError(f"{child}: unknown {fk}")
    if not orders["order_id"].isin(items["order_id"]).all():
        raise ValueError("orders: every order needs at least one item")
    if not orders["status"].isin(["delivered", "returned", "cancelled"]).all():
        raise ValueError("orders: unsupported status")
    pd.to_datetime(orders["order_date"], format="%Y-%m-%d", errors="raise")
    for column in ["quantity", "unit_price", "unit_cost", "discount_rate"]:
        items[column] = pd.to_numeric(items[column], errors="raise")
    if ((items["quantity"] <= 0) | (items["quantity"] % 1 != 0) |
        (items["unit_price"] < 0) | (items["unit_cost"] < 0) |
        ~items["discount_rate"].between(0, 1)).any():
        raise ValueError("order_items: invalid quantity, price, cost or discount")
    with sqlite3.connect(":memory:") as connection:
        for name, frame in tables.items():
            frame.to_sql(name, connection, index=False)
        lines = pd.read_sql_query((ROOT / "sql" / "order_lines.sql").read_text(), connection)
    lines["order_date"] = pd.to_datetime(lines["order_date"])
    lines["profit"] = (lines["revenue"] - lines["cost"]).round(2)
    return lines, {name: len(frame) for name, frame in tables.items()}
