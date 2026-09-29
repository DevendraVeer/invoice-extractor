# Invoice Tracker

A small backend project to store, load, and analyze business invoices using Python and PostgreSQL.

## What it does
- Stores vendors, invoices, and line items in a normalized PostgreSQL schema (3 related tables).
- Loads invoice data from a CSV file using a Python script.
- The loader is idempotent — running it multiple times does not create duplicate data. It clears and rebuilds each invoice's line items on every run, so the database always matches the current CSV.
- Answers 5 real business questions using SQL: monthly spend, top vendors, above-average invoices, month-over-month spend change (using a window function), and duplicate invoice detection.

## Why 3 tables
One vendor can have many invoices, and one invoice can have many line items. Splitting these into `vendors`, `invoices`, and `line_items` avoids repeating vendor/invoice data on every line item row, and lets each table enforce its own rules (e.g. a vendor name must be unique, an invoice number must be unique per vendor).

## Tech stack
- Python (psycopg, python-dotenv)
- PostgreSQL

## Setup
1. Create a PostgreSQL database named `invoices`.
2. Add a `.env` file with:
  DATABASE_URL=postgresql://postgres:YOURPASS@localhost:5432/invoices
3. Run the schema:

Run schema.sql in pgAdmin's Query Tool (or psql -f schema.sql)

4. Load the data:

python load.py

5. 5. Run the reports in `reports.sql` using pgAdmin's Query Tool.


## What I'd add next
- A FastAPI layer to expose this data over HTTP endpoints.
- A React dashboard to visualize the reports.
- LLM-based extraction to auto-fill invoice data from scanned/uploaded invoices instead of manual CSV entry.
    
