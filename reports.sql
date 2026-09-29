-- Report 1: Total spend per month
SELECT
    DATE_TRUNC('month', invoice_date) AS month,
    SUM(total) AS total_spend
FROM invoices
GROUP BY DATE_TRUNC('month', invoice_date)
ORDER BY DATE_TRUNC('month', invoice_date);

-- Report 2: Top 5 vendors by total spend
SELECT v.name, SUM(i.total) AS total_spend
FROM invoices i
JOIN vendors v ON i.vendor_id = v.id
GROUP BY v.name
ORDER BY total_spend DESC
LIMIT 5;

-- Report 3: Invoices above the average invoice value
SELECT invoice_no, total
FROM invoices
WHERE total > (SELECT AVG(total) FROM invoices);

-- Report 4: Month-over-month change in spend
SELECT
    DATE_TRUNC('month', invoice_date) AS month,
    SUM(total) AS total_spend,
    LAG(SUM(total)) OVER (
        ORDER BY DATE_TRUNC('month', invoice_date)
    ) AS prev_month_spend
FROM invoices
GROUP BY DATE_TRUNC('month', invoice_date)
ORDER BY DATE_TRUNC('month', invoice_date);

-- Report 5: Possible duplicate invoices
SELECT vendor_id, invoice_date, total, COUNT(*) AS how_many
FROM invoices
GROUP BY vendor_id, invoice_date, total
HAVING COUNT(*) > 1;