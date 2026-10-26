CREATE TABLE customers(id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE invoices(id INTEGER PRIMARY KEY, customer_id INTEGER, total_cents INTEGER, status TEXT);
CREATE TABLE payments(id INTEGER PRIMARY KEY, invoice_id INTEGER, amount_cents INTEGER, status TEXT);
CREATE TABLE credits(id INTEGER PRIMARY KEY, invoice_id INTEGER, amount_cents INTEGER, status TEXT);