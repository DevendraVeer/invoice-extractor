import os 
import psycopg
from  dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date


class LineItemIn(BaseModel):
    description: str
    qty: float
    unit_price: float

class InvoiceIn(BaseModel):
    vendor_name: str
    gstin: str | None = None
    invoice_no: str
    invoice_date: date
    line_items: list[LineItemIn]








load_dotenv()
DSN = os.environ["DATABASE_URL"]

app = FastAPI()


@app.post("/invoices")
def create_invoice(invoice: InvoiceIn):
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO vendors (name, gstin)
                VALUES (%s, %s)
                ON CONFLICT (name) DO UPDATE SET gstin = EXCLUDED.gstin
                RETURNING id;""",(invoice.vendor_name, invoice.gstin)
            )
            vendor_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO invoices (vendor_id, invoice_no, invoice_date)
                VALUES (%s, %s, %s)
                ON CONFLICT (vendor_id, invoice_no) DO UPDATE SET invoice_date = EXCLUDED.invoice_date
                RETURNING id;
            """, (vendor_id, invoice.invoice_no, invoice.invoice_date))
            invoice_id = cur.fetchone()[0]

            cur.execute("DELETE FROM line_items WHERE invoice_id = %s;", (invoice_id,))
            for item in invoice.line_items:
                cur.execute("""
                    INSERT INTO line_items (invoice_id, description, qty, unit_price)
                    VALUES (%s, %s, %s, %s);
                """, (invoice_id, item.description, item.qty, item.unit_price))

            cur.execute("""
                UPDATE invoices i SET total = s.t
                FROM (SELECT invoice_id, SUM(qty * unit_price) AS t
                      FROM line_items GROUP BY invoice_id) s
                WHERE i.id = s.invoice_id;
            """)
        conn.commit()
    return {"invoice_id": invoice_id, "vendor_id": vendor_id, "status": "created"}









@app.get("/")
def home():
    return{"status": "invoice tracker API is running successfully"}

@app.get("/reports/monthly")
def monthly_spend():
    with psycopg.connect(DSN) as conn:
        rows= conn.execute("""
            SELECT
                DATE_TRUNC('month', invoice_date) AS month,
                SUM(total) AS total_spend
            FROM invoices
            GROUP BY DATE_TRUNC('month', invoice_date)
            ORDER BY DATE_TRUNC('month', invoice_date);
"""
        ).fetchall()

    return [{"month": str(r[0]), "total_spend": float(r[1])} for r in rows]

@app.get("/reports/top-vendors")

def top_vendors():
    with psycopg.connect(DSN) as conn:
        rows=conn.execute("""
            SELECT v.name, SUM(i.total) AS total_spend
FROM invoices i
JOIN vendors v ON i.vendor_id = v.id
GROUP BY v.name
ORDER BY total_spend DESC
LIMIT 5;
"""

        ).fetchall()

    return[{"name":r[0] , "total_spend": float(r[1])} for r in rows]

@app.get("/reports/above-average")
def above_average_invoices():
    with psycopg.connect(DSN) as conn:
        rows= conn.execute("""
            SELECT invoice_no, total
FROM invoices
WHERE total > (SELECT AVG(total) FROM invoices);

     """   ).fetchall()


    return [{"invoice_no": r[0], "total": float(r[1])} for r in rows]


@app.get("/reports/months-over-month")

def month_over_month():
    with psycopg.connect(DSN) as conn:
        rows= conn.execute("""
            SELECT
    DATE_TRUNC('month', invoice_date) AS month,
    SUM(total) AS total_spend,
    LAG(SUM(total)) OVER (
        ORDER BY DATE_TRUNC('month', invoice_date)
    ) AS prev_month_spend
FROM invoices
GROUP BY DATE_TRUNC('month', invoice_date)
ORDER BY DATE_TRUNC('month', invoice_date);
      """  ).fetchall()

    return[{"month": str(r[0]), "total_spend": float(r[1]), "prev_month_spend": float(r[2] if r[2] else None)} for r in rows]


@app.get("/reports/duplicates")

def possible_duplicates():
    with psycopg.connect(DSN) as conn:
        rows = conn.execute("""
            SELECT vendor_id, invoice_date, total, COUNT(*) AS how_many
FROM invoices
GROUP BY vendor_id, invoice_date, total
HAVING COUNT(*) > 1;
     """   ).fetchall()

    return[{"vendorid": r[0],"invoice_date": str(r[1]), "total": float(r[2]), "how_many": r[3]} for r in rows]
