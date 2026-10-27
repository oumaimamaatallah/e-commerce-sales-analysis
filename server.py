import json
import os
from datetime import date
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
import pandas as pd

from analysis.data import ROOT, load_data
from analysis.metrics import summarize, customer_segments, cohort_retention

app = FastAPI(title="Sunday Supply / Sales journal", docs_url="/api/docs")


@lru_cache(maxsize=1)
def dataset():
    return load_data(os.environ.get("DATA_DIR"))


def records(frame):
    return json.loads(frame.to_json(orient="records", date_format="iso"))


def selection(start=None, end=None, country="all", channel="all", category="all"):
    lines, _ = dataset()
    mask = pd.Series(True, index=lines.index)
    if start:
        mask &= lines.order_date.ge(pd.Timestamp(start))
    if end:
        mask &= lines.order_date.le(pd.Timestamp(end))
    for column, value in [("country", country), ("channel", channel), ("category", category)]:
        if value != "all":
            mask &= lines[column].eq(value)
    return lines[mask].copy()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/meta")
def metadata():
    lines, counts = dataset()
    return {"countries": sorted(lines.country.unique()), "channels": sorted(lines.channel.unique()),
            "categories": sorted(lines.category.unique()),
            "start": str(lines.order_date.min().date()), "end": str(lines.order_date.max().date()),
            "tables": counts, "source": "Synthetic retail sample / seed 42 / EUR"}


@app.get("/api/dashboard")
def dashboard(start: date | None = None, end: date | None = None,
              country: str = "all", channel: str = "all", category: str = "all"):
    lines = selection(start, end, country, channel, category)
    full, _ = dataset()
    delivered = lines[lines.status.eq("delivered")]
    monthly = lines.assign(month=lines.order_date.dt.to_period("M").dt.to_timestamp()).groupby("month", as_index=False).agg(
        revenue=("revenue", "sum"), profit=("profit", "sum"), orders=("order_id", "nunique"))
    products = delivered.groupby(["product_name", "category"], as_index=False).agg(
        revenue=("revenue", "sum"), profit=("profit", "sum"), units=("quantity", "sum"))
    products["margin"] = products.profit.div(products.revenue.where(products.revenue.ne(0))).fillna(0)
    categories = delivered.groupby("category", as_index=False).revenue.sum()
    channels = delivered.groupby("channel", as_index=False).agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"))
    customers = customer_segments(lines, full.order_date.max() + pd.Timedelta(days=1))
    segments = customers.groupby("segment", as_index=False).agg(customers=("customer_id", "size"), revenue=("monetary", "sum"))
    retention = cohort_retention(lines)
    orders = lines.groupby("order_id", as_index=False).agg(
        order_date=("order_date", "first"), customer_id=("customer_id", "first"), country=("country", "first"),
        channel=("channel", "first"), status=("status", "first"), revenue=("revenue", "sum"),
        units=("quantity", "sum"), item_rows=("product_id", "size"))
    return {
        "summary": summarize(lines), "line_count": len(lines), "order_count": len(orders),
        "monthly": records(monthly), "products": records(products.sort_values("revenue", ascending=False)),
        "categories": records(categories), "channels": records(channels.sort_values("revenue", ascending=False)),
        "segments": records(segments), "customers": records(customers.sort_values("monetary", ascending=False)),
        "cohorts": {"labels": list(retention.index), "ages": list(retention.columns),
                    "values": json.loads(retention.to_json(orient="values"))},
        "orders": records(orders.sort_values(["order_date", "order_id"], ascending=False)),
    }


@app.get("/api/export")
def export(start: date | None = None, end: date | None = None,
           country: str = "all", channel: str = "all", category: str = "all"):
    lines = selection(start, end, country, channel, category)
    return Response(lines.to_csv(index=False), media_type="text/csv",
                    headers={"Content-Disposition": 'attachment; filename="selected_order_lines.csv"'})


@app.get("/api/model")
def model():
    return {"sql": (ROOT / "sql/order_lines.sql").read_text(),
            "revenue": "Delivered item value after discounts. Returned and cancelled orders produce zero revenue.",
            "margin": "(Delivered revenue - item costs) / delivered revenue. Tax, shipping and overhead are excluded.",
            "aov": "Selected delivered item revenue / distinct delivered order IDs.",
            "repeat": "Customers with at least two distinct delivered orders / buying customers in the selection.",
            "cohorts": "First delivered purchase within the selection. Observed inactive months are zero; future months are blank."}


if (ROOT / "static/index.html").exists():
    app.mount("/", StaticFiles(directory=ROOT / "static", html=True), name="frontend")
