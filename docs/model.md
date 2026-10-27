# Data & metrics

The CSV files are generated locally with `scripts/generate_data.py` (seed 42). There are no external downloads, customer names or real transactions. The store has 600 customer IDs, 24 products and 2,400 orders over January–December 2025. Some customers never buy; purchasing is intentionally uneven and November has higher sampling weight. These patterns are assumptions in a demo, not discoveries about real retail.

| File | Grain / key | Fields |
| --- | --- | --- |
| customers.csv | Customer / customer_id | country |
| products.csv | Product / product_id | product_name, category, list_price, unit_cost |
| orders.csv | Order / order_id | customer_id, order_date (YYYY-MM-DD), channel, status |
| order_items.csv | Order × product / (order_id, product_id) | quantity, unit_price, unit_cost, discount_rate (0–1) |

`orders` joins to `customers` and `order_items`, which joins to `products`. The SQL model produces one row per item, preserving the price and cost recorded on the item. Dimension keys, foreign keys, statuses, dates and numeric ranges are checked before joining.

| Metric | Definition |
| --- | --- |
| Line value | round(quantity × unit_price × (1 − discount_rate), 2) |
| Net revenue | Sum of line values for delivered orders |
| Gross profit | Delivered revenue − delivered item costs |
| Gross margin | Gross profit / revenue |
| Delivered orders | Distinct delivered order IDs |
| Average order value | Revenue / delivered orders |
| Return rate | Distinct returned orders / distinct delivered or returned orders |
| Refunds | Item value on fully returned orders |
| Repeat customer rate | Customers with ≥2 distinct delivered orders / customers with ≥1 |

VAT, shipping, acquisition costs, partial returns and overheads are outside the model. All values are EUR; money is rounded at line level. Zero denominators return zero.

Dashboard filters affect every tab and export. Category selection means AOV is selected-category spending per order containing that category, rather than full basket value.

The customer table calculates frequency and spend inside the selection. Recency is measured as of the day after the full dataset's last order. Rules are applied in this order: default One-time; Repeat if ≥2 orders; At risk if recency >120 days; Champions if ≥3 orders, recency ≤90 days and spend ≥80th percentile. These are explainable heuristic groups, not a fitted prediction model.

Cohort month is the customer's first delivered purchase **within the selection**. Retention is the share of that cohort purchasing in each later calendar month. Observed months with no purchases are zero; months after the last selected transaction are blank. This does not estimate lifetime value or claim to observe a customer's earlier history.

Tests use small, hand-calculated examples for multi-line orders, returns, cancellations and cohort gaps. The SQL is in `sql/order_lines.sql`; formulas are in `analysis/metrics.py`.
