-- Grain: one product line per order. Cancelled and returned orders produce no revenue.
SELECT o.order_id, o.customer_id, o.order_date, o.channel, o.status,
       c.country, p.product_id, p.product_name, p.category,
       i.quantity, i.unit_price, i.unit_cost, i.discount_rate,
       ROUND(i.quantity * i.unit_price, 2) AS gross_amount,
       ROUND(i.quantity * i.unit_price * i.discount_rate, 2) AS discount_amount,
       ROUND(i.quantity * i.unit_price * (1 - i.discount_rate), 2) AS line_value,
       CASE WHEN o.status = 'delivered'
            THEN ROUND(i.quantity * i.unit_price * (1 - i.discount_rate), 2)
            ELSE 0 END AS revenue,
       CASE WHEN o.status = 'delivered'
            THEN ROUND(i.quantity * i.unit_cost, 2) ELSE 0 END AS cost
FROM orders AS o
JOIN customers AS c ON c.customer_id = o.customer_id
JOIN order_items AS i ON i.order_id = o.order_id
JOIN products AS p ON p.product_id = i.product_id
ORDER BY o.order_date, o.order_id, p.product_id;
