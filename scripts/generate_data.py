"""Create the bundled fictional retail dataset. No third-party dependencies."""

import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def generate(output, seed=42):
    rng = random.Random(seed)
    customers = [
        {"customer_id": f"C{i:04d}", "country": rng.choices(
            ["Germany", "France", "Netherlands", "Belgium"], [52, 25, 15, 8])[0]}
        for i in range(1, 601)
    ]
    catalog = {
        "Home": ["Desk lamp", "Linen throw", "Ceramic vase", "Storage basket", "Wall clock", "Cushion"],
        "Kitchen": ["Coffee grinder", "Glass carafe", "Bowl set", "Cutting board", "Tea pot", "Lunch box"],
        "Accessories": ["Canvas tote", "Travel pouch", "Card holder", "Wool scarf", "Umbrella", "Key ring"],
        "Stationery": ["Weekly planner", "Notebook", "Pen set", "Desk tray", "Pencil case", "Bookmark set"],
    }
    products = []
    for category, names in catalog.items():
        for name in names:
            price = rng.choice([12, 18, 24, 32, 48, 64, 89])
            products.append({"product_id": f"P{len(products)+1:03d}", "product_name": name,
                             "category": category, "list_price": price,
                             "unit_cost": round(price * rng.uniform(.36, .68), 2)})
    orders, items = [], []
    # Repeat purchasing is intentionally uneven, rather than one order per customer.
    weights = [6 if i < 90 else 1 for i in range(len(customers))]
    for i in range(1, 2401):
        month = rng.choices(range(1, 13), [7, 7, 8, 8, 8, 7, 7, 8, 9, 11, 17, 14])[0]
        order_date = date(2025, month, 1) + timedelta(days=rng.randrange(28))
        customer = rng.choices(customers, weights)[0]
        channel = rng.choices(["Organic", "Paid search", "Email", "Social"], [37, 30, 21, 12])[0]
        status = rng.choices(["delivered", "returned", "cancelled"], [87, 8, 5])[0]
        orders.append({"order_id": f"O{i:05d}", "customer_id": customer["customer_id"],
                       "order_date": order_date.isoformat(), "channel": channel, "status": status})
        for product in rng.sample(products, k=rng.choices([1, 2, 3, 4], [45, 32, 18, 5])[0]):
            discount = rng.choices([0, .1, .2, .3], [52, 25, 18, 5])[0]
            items.append({"order_id": f"O{i:05d}", "product_id": product["product_id"],
                          "quantity": rng.choices([1, 2, 3], [80, 16, 4])[0],
                          "unit_price": product["list_price"], "unit_cost": product["unit_cost"],
                          "discount_rate": discount})
    for filename, rows in [("customers.csv", customers), ("products.csv", products),
                           ("orders.csv", orders), ("order_items.csv", items)]:
        write_csv(output / filename, rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "data")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    generate(args.output, args.seed)
    print(f"Wrote fictional retail data to {args.output}")
