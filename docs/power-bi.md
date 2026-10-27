# Power BI

The browser dashboard uses React and Recharts; it is not a `.pbix` report. Power BI Desktop is optional.

Run `python run.py --export`. In Power BI Desktop, use **Get data â†’ Text/CSV** to load `exports/order_lines.csv`. Set `order_date` to Date and the amount fields to Decimal number. Keep the item-row grain; use distinct counts for orders and customers.

```dax
Net revenue = SUM(order_lines[revenue])
Gross profit = SUM(order_lines[profit])
Gross margin = DIVIDE([Gross profit], [Net revenue], 0)
Delivered orders = CALCULATE(DISTINCTCOUNT(order_lines[order_id]), order_lines[status] = "delivered")
Average order value = DIVIDE([Net revenue], [Delivered orders], 0)
```

Use cards for these measures, a line chart by `order_date`, and bars by `category` or `channel`. Add date, country and category slicers. These measures follow the same selected-item semantics as the app.

For customer segments, import `customer_segments.csv`. For cohorts, import `cohort_retention.csv`; values are fractions (0â€“1), and blank cells are future periods. Both are static exports and do not recalculate their grouping when a Power BI slicer changes. Regenerate them for a different source dataset.

Colors: navy `#1B314A`, teal `#197873`, gold `#D5A448`, background `#F5F6F8`.
