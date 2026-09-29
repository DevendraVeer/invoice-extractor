# Invoice Tracker

A small backend project to store, load, analyze, and serve business invoice data using Python, PostgreSQL, and FastAPI.

## What it does
- Stores vendors, invoices, and line items in a normalized PostgreSQL schema (3 related tables).
- Loads invoice data from a CSV file using a Python script.
- The loader is idempotent — running it multiple times does not create duplicate data. It clears and rebuilds each invoice's line items on every run, so the database always matches the current CSV.
- Exposes the data over a REST API built with FastAPI, so it can be read and written over HTTP instead of only through scripts.
- Answers 5 real business questions using SQL: monthly spend, top vendors, above-average invoices, month-over-month spend change (using a window function), and duplicate invoice detection.

## Why 3 tables
One vendor can have many invoices, and one invoice can have many line items. Splitting these into `vendors`, `invoices`, and `line_items` avoids repeating vendor/invoice data on every line item row, and lets each table enforce its own rules (e.g. a vendor name must be unique, an invoice number must be unique per vendor).

## The idempotency problem (and fix)
The first version of the loader inserted line items with a plain `INSERT`, with no protection against re-running. Running it twice doubled every line item, because vendors and invoices were protected with `ON CONFLICT` but line items weren't (line items have no natural unique identity — two identical items can legitimately exist on one invoice). 

Fix: **delete-and-replace**. Before inserting an invoice's line items (the first time that invoice is seen in a given run), any existing line items for that invoice are deleted, then the current set is inserted fresh. This makes both `load.py` and the `POST /invoices` endpoint safe to call repeatedly — the database always ends up matching whatever was just sent in, no duplicates, no manual cleanup.

## Tech stack
- Python (FastAPI, psycopg, python-dotenv, Pydantic)
- PostgreSQL
- Uvicorn (ASGI server)

## Setup
1. Create a PostgreSQL database named `invoices`.
2. Add a `.env` file with:

DATABASE_URL=postgresql://postgres:YOURPASS@localhost:5432/invoices

3. Install dependencies:

pip install fastapi uvicorn psycopg[binary] python-dotenv pydantic

4. Run the schema:

Run schema.sql in pgAdmin's Query Tool (or psql -f schema.sql)

5. Load sample data:

python load.py

6. Start the API:

uvicorn main:app --reload

7. Open `http://127.0.0.1:8000/docs` for interactive API docs.

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/reports/monthly` | Total spend per month |
| GET | `/reports/top-vendors` | Top 5 vendors by total spend |
| GET | `/reports/above-average` | Invoices above the average invoice value |
| GET | `/reports/month-over-month` | Monthly spend with previous month for comparison |
| GET | `/reports/duplicates` | Invoices with matching vendor, date, and total (possible duplicates) |
| POST | `/invoices` | Create or update an invoice with its line items |

### Example: create an invoice

POST /invoices
Content-Type: application/json

{
"vendor_name": "Test Vendor",
"gstin": "27TEST1234F1Z5",
"invoice_no": "INV-999",
"invoice_date": "2026-09-15",
"line_items": [
{"description": "Test item", "qty": 2, "unit_price": 100}
]
}





## What I'd add next
- A React dashboard calling these endpoints directly.
- LLM-based extraction to auto-fill invoice data from scanned/uploaded invoices instead of manual entry.
- Auth (API key or JWT) before exposing this publicly.