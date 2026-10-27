import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from analysis.data import ROOT, load_data
from analysis.metrics import cohort_retention, customer_segments, summarize
from analysis.ui import COLORS, GOLD, NAVY, TEAL, chart, empty, metric_row, money, setup

setup("Sales & customer behavior", "Revenue, product margins and repeat purchasing · 2025 retail sample", "◈")
with st.sidebar:
    st.subheader("RETAIL / 01")
    st.caption("A small store. A full year of orders.")
    st.divider()
try:
    lines, row_counts = load_data(os.environ.get("DATA_DIR"))
except (ValueError, FileNotFoundError, KeyError) as error:
    st.error(f"Could not load the dataset: {error}")
    st.stop()

with st.sidebar:
    dates = st.date_input("Order dates", value=(lines.order_date.min().date(), lines.order_date.max().date()),
                          min_value=lines.order_date.min().date(), max_value=lines.order_date.max().date(), key="dates")
    countries = st.multiselect("Country", sorted(lines.country.unique()), default=sorted(lines.country.unique()), key="countries")
    channels = st.multiselect("Channel", sorted(lines.channel.unique()), default=sorted(lines.channel.unique()), key="channels")
    categories = st.multiselect("Category", sorted(lines.category.unique()), default=sorted(lines.category.unique()), key="categories")
    st.divider()
    st.caption("EUR · synthetic data · no personal data")
    st.caption("Revenue excludes returns and cancellations. Filters apply to every tab and export.")

if len(dates) != 2:
    st.info("Choose both a start and an end date.")
    st.stop()
start, end = map(pd.Timestamp, dates)
selected = lines[lines.order_date.between(start, end) & lines.country.isin(countries) &
                 lines.channel.isin(channels) & lines.category.isin(categories)].copy()
if selected.empty:
    empty()
summary = summarize(selected)
metric_row([
    ("Net revenue", money(summary["revenue"]), "Delivered items after discounts; excludes VAT, shipping and returned orders."),
    ("Delivered orders", f"{summary['orders']:,}", "Distinct delivered order IDs, not item rows."),
    ("Average order value", money(summary["aov"]), "Selected delivered item revenue / distinct delivered orders."),
    ("Gross margin", f"{summary['margin']:.1%}", "(Revenue − item cost) / revenue. Operating costs are not included."),
])
overview, customers, data_tab = st.tabs(["Sales overview", "Customers", "Data & SQL"])
delivered = selected[selected.status.eq("delivered")].copy()

with overview:
    left, right = st.columns([1.65, 1])
    with left:
        monthly = selected.assign(month=selected.order_date.dt.to_period("M").dt.to_timestamp()).groupby("month", as_index=False)[["revenue", "profit"]].sum()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=monthly.month, y=monthly.revenue, name="Net revenue", mode="lines+markers", line={"color": TEAL, "width": 3}, fill="tozeroy", fillcolor="rgba(25,120,115,.07)"))
        fig.add_trace(go.Scatter(x=monthly.month, y=monthly.profit, name="Gross profit", mode="lines", line={"color": GOLD, "width": 2}))
        fig.update_layout(title="Revenue & gross profit", yaxis_tickprefix="€", legend={"orientation": "h", "y": -.2})
        chart(fig, "monthly")
    with right:
        by_category = delivered.groupby("category", as_index=False).revenue.sum().sort_values("revenue")
        fig = px.bar(by_category, x="revenue", y="category", orientation="h", title="Revenue by category", color_discrete_sequence=[TEAL])
        fig.update_layout(xaxis_title="EUR", yaxis_title=None)
        chart(fig, "category")
    left, right = st.columns([1.15, 1.5])
    with left:
        channel = delivered.groupby("channel", as_index=False).agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"))
        fig = px.bar(channel, x="channel", y="revenue", title="Revenue by acquisition channel", color_discrete_sequence=[NAVY], hover_data=["orders"])
        fig.update_layout(xaxis_title=None, yaxis_title="EUR")
        chart(fig, "channel")
    with right:
        products = delivered.groupby(["product_name", "category"], as_index=False).agg(revenue=("revenue", "sum"), profit=("profit", "sum"), units=("quantity", "sum"))
        products["margin_pct"] = products.profit.div(products.revenue.where(products.revenue.ne(0))).mul(100).fillna(0)
        st.subheader("Products to watch")
        st.caption("Top products by selected revenue. Margin includes item cost only.")
        st.dataframe(products.sort_values("revenue", ascending=False).head(8), hide_index=True, width="stretch",
                     column_config={"revenue": st.column_config.NumberColumn("Revenue €", format="%.2f"),
                                    "profit": st.column_config.NumberColumn("Profit €", format="%.2f"),
                                    "margin_pct": st.column_config.NumberColumn("Margin %", format="%.1f")})
    st.caption(f"Returns: {summary['return_rate']:.1%} of resolved orders · Refunded item value: {money(summary['refunds'])} · Cancelled orders excluded from the return-rate denominator.")

with customers:
    metric_row([
        ("Buying customers", f"{summary['customers']:,}", "Distinct customers with a delivered order in the selection."),
        ("Repeat customer rate", f"{summary['repeat_rate']:.1%}", "Customers with at least two distinct delivered orders / buying customers in the selection."),
        ("Gross profit", money(summary["profit"]), "Net delivered revenue less item costs."),
    ])
    segments = customer_segments(selected, lines.order_date.max() + pd.Timedelta(days=1))
    a, b = st.columns([1, 1.6])
    with a:
        sizes = segments.groupby("segment", as_index=False).size()
        chart(px.bar(sizes, x="size", y="segment", orientation="h", title="Customer groups", color="segment", color_discrete_sequence=COLORS).update_layout(showlegend=False, xaxis_title="Customers", yaxis_title=None), "segments")
    with b:
        retention = cohort_retention(selected)
        if not retention.empty:
            fig = go.Figure(go.Heatmap(z=retention.values * 100, x=[f"M{age}" for age in retention.columns], y=retention.index,
                                      colorscale=[[0, "#F0F5F4"], [1, TEAL]], zmin=0, zmax=100,
                                      hovertemplate="Cohort %{y}<br>%{x}: %{z:.1f}%<extra></extra>", colorbar={"title": "%"}))
            chart(fig.update_layout(title="Monthly repeat purchasing by cohort", yaxis_autorange="reversed"), "retention")
        else:
            st.info("This selection has no delivered orders for a cohort analysis.")
    st.caption("Cohorts use each customer's first delivered order within the selection. M0 = 100%; future months are blank. This is observed repeat purchasing, not a forecast.")
    with st.expander("Segment rules & customer-level table"):
        st.write("Champions: ≥3 orders, recency ≤90 days and spend in the top 20%. At risk: recency >120 days. Repeat: ≥2 orders. Otherwise: One-time. Recency is measured from the day after the dataset ends; frequency and spend use the selection.")
        st.dataframe(segments, hide_index=True, width="stretch")
        st.download_button("Download customer segments", segments.to_csv(index=False).encode(), "customer_segments.csv", "text/csv")

with data_tab:
    st.subheader("Order-line audit")
    st.caption(f"{len(selected):,} selected item rows · {selected.order_id.nunique():,} distinct orders · raw table sizes: {row_counts}")
    st.dataframe(selected, hide_index=True, width="stretch", height=380)
    st.download_button("Download selected order lines", selected.to_csv(index=False).encode(), "order_lines.csv", "text/csv")
    with st.expander("SQL behind the model"):
        st.code((ROOT / "sql" / "order_lines.sql").read_text(), language="sql")
    st.caption("The bundled dataset is fictional and reproducible with seed 42. This dashboard does not measure acquisition cost, conversion, tax, shipping, or customer lifetime value.")
