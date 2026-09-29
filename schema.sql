 create table vendors(
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    gstin TEXT
 );

 create table invoices(

    id SERIAL PRIMARY KEY,
    vendor_id INT NOT NULL REFERENCES vendors(id),
    invoice_no TEXT NOT NULL,
    invoice_date TEXT NOT NULL,
    total NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK(total>=0),
    UNIQUE (vendor_id,invoice_no)
 );

 CREATE TABLE line_items(
    id SERIAL PRIMARY KEY,
    invoice_id INT NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    qty NUMERIC(10,2) NOT NULL,
    unit_price NUMERIC(12,2) not NULL




 );

 CREATE INDEX idx_invoices_date  on invoices(invoice_date);