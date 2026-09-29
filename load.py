import csv
import os
import psycopg
from dotenv import load_dotenv


load_dotenv()
DSN = os.environ["DATABASE_URL"]


def get_or_create_vendor(cur,name,gstin):
    cur.execute("""
        INSERT INTO VENDORS(name,gstin)
        VALUES (%s,%s)
        ON CONFLICT (name) DO UPDATE SET gstin = EXCLUDED.gstin
        RETURNING id;
    """, (name,gstin))

    return cur.fetchone()[0]
        


def get_or_create_invoice(cur,vendor_id,invoice_no,invoice_date):
    cur.execute("""
        INSERT INTO invoices (vendor_id,invoice_no,invoice_date)
        VALUES(%s,%s,%s)
        ON CONFLICT(vendor_id,invoice_no) DO UPDATE SET invoice_date= EXCLUDED.invoice_date
        RETURNING id;
    """,(vendor_id,invoice_no,invoice_date) )

    return cur.fetchone()[0]


def insert_line_item(cur,invoice_id,description,qty,unit_price):
    cur.execute("""
        INSERT INTO line_items(invoice_id,description,qty,unit_price)
        VALUES(%s,%s,%s,%s)
        """,(invoice_id,description,qty,unit_price)
    )

def clear_line_items(cur, invoice_id):
    cur.execute("DELETE FROM line_items WHERE invoice_id = %s;", (invoice_id,))


def recalc_totals(cur):
    cur.execute("""
        UPDATE invoices i SET TOTAL = s.t
        FROM (
            SELECT invoice_id, SUM(qty * unit_price) AS t
            FROM line_items
            GROUP BY invoice_id
        ) s

        WHERE i.id = s.invoice_id;
        """
    )

def main():
        with psycopg.connect(DSN) as conn:
            with conn.cursor() as cur:
                cleared_invoices = set()
                with open("data/invoices.csv", newline="") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        vendor_id = get_or_create_vendor(cur, row["vendor"], row["gstin"])
                        invoice_id= get_or_create_invoice(cur,vendor_id,row["invoice_no"],row["invoice_date"])

                        if invoice_id not in cleared_invoices:      # NEW
                            clear_line_items(cur, invoice_id)       # NEW
                            cleared_invoices.add(invoice_id)        

                        insert_line_item(cur, invoice_id,row["description"], row["qty"], row["unit_price"])

                recalc_totals(cur)
            conn.commit()
        print("Done loading invoices")

if __name__=="__main__":
    main()
    
