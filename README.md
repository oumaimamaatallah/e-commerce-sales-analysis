# Sunday Supply / Sales journal

A retail dashboard for revenue, margins and repeat purchasing. Its quiet ledger layout keeps the numbers close to the orders behind them.

![Sales journal](docs/dashboard.png)

## Run

Python 3.11-3.13:

    python run.py

Open http://localhost:8501. The launcher installs the pinned Python dependencies on first use. The React frontend is bundled, so Node.js is only needed for frontend development.

    python run.py --test
    python run.py --export

Try the country and category filters, open the customer cohorts, then follow an order in the order book. CSV exports follow the current selection.

The sample contains 2,400 synthetic orders in 2025, generated with seed 42. Amounts are EUR; returns and cancellations produce no recognized revenue.

[Setup and dependencies](docs/setup.md) / [Data and metrics](docs/model.md) / [Power BI import](docs/power-bi.md)
