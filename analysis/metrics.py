import pandas as pd


def summarize(lines):
    delivered = lines[lines["status"].eq("delivered")]
    returned = lines[lines["status"].eq("returned")]
    count = delivered["order_id"].nunique()
    resolved = lines[lines["status"].ne("cancelled")]["order_id"].nunique()
    revenue, profit = delivered["revenue"].sum(), delivered["profit"].sum()
    frequency = delivered.groupby("customer_id")["order_id"].nunique()
    return {
        "revenue": round(float(revenue), 2), "orders": count, "profit": round(float(profit), 2),
        "aov": float(revenue / count) if count else 0,
        "margin": float(profit / revenue) if revenue else 0,
        "return_rate": returned["order_id"].nunique() / resolved if resolved else 0,
        "customers": len(frequency),
        "repeat_rate": float(frequency.ge(2).mean()) if len(frequency) else 0,
        "refunds": round(float(returned["line_value"].sum()), 2),
    }


def customer_segments(lines, as_of):
    delivered = lines[lines["status"].eq("delivered")]
    customers = delivered.groupby("customer_id").agg(
        last_order=("order_date", "max"), frequency=("order_id", "nunique"),
        monetary=("revenue", "sum")).reset_index()
    customers["recency_days"] = (pd.Timestamp(as_of) - customers["last_order"]).dt.days
    customers["segment"] = "One-time"
    customers.loc[customers["frequency"].ge(2), "segment"] = "Repeat"
    customers.loc[customers["recency_days"].gt(120), "segment"] = "At risk"
    threshold = customers["monetary"].quantile(.8)
    customers.loc[customers["frequency"].ge(3) & customers["recency_days"].le(90) &
                  customers["monetary"].ge(threshold), "segment"] = "Champions"
    return customers


def cohort_retention(lines):
    """First purchase and activity are measured within the current selection."""
    activity = lines[lines["status"].eq("delivered")][["customer_id", "order_date"]].copy()
    if activity.empty:
        return pd.DataFrame()
    activity["month"] = activity["order_date"].dt.to_period("M")
    activity["cohort"] = activity.groupby("customer_id")["month"].transform("min")
    activity["age"] = (activity["month"].astype("int64") - activity["cohort"].astype("int64"))
    counts = activity.groupby(["cohort", "age"])["customer_id"].nunique().unstack()
    # Missing periods already observed are zero; future periods stay blank.
    last = activity["month"].max()
    counts = counts.reindex(columns=range(last.ordinal - counts.index.min().ordinal + 1))
    for cohort in counts.index:
        observed = last.ordinal - cohort.ordinal
        for age in counts.columns:
            if age <= observed and pd.isna(counts.loc[cohort, age]):
                counts.loc[cohort, age] = 0
    retention = counts.div(counts[0], axis=0)
    retention.index = retention.index.astype(str)
    return retention
