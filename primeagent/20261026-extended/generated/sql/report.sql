-- report.sql — read-only customer ledger. One SELECT, no writes, no mutations.
-- Grain rule: payments and credits are summed per invoice_id first (GROUP BY),
-- then joined 1:1 to the issued invoice, so an invoice with N payments and M
-- credits never multiplies its total (or vice versa).
-- Only status='issued' invoices count; payments must be 'posted', credits 'approved'.
WITH issued_invoice AS (
  SELECT
    inv.id AS invoice_id,
    inv.customer_id AS customer_id,
    inv.total_cents AS total_cents
  FROM invoices AS inv
  WHERE inv.status = 'issued'
), posted_sums AS (
  SELECT
    pay.invoice_id AS invoice_id,
    SUM(pay.amount_cents) AS posted_cents
  FROM payments AS pay
  WHERE pay.status = 'posted'
  GROUP BY pay.invoice_id
), approved_sums AS (
  SELECT
    crd.invoice_id AS invoice_id,
    SUM(crd.amount_cents) AS approved_cents
  FROM credits AS crd
  WHERE crd.status = 'approved'
  GROUP BY crd.invoice_id
), per_invoice AS (
  SELECT
    issued_invoice.invoice_id AS invoice_id,
    issued_invoice.customer_id AS customer_id,
    issued_invoice.total_cents AS total_cents,
    COALESCE(pst.posted_cents, 0) AS posted_cents,
    COALESCE(apr.approved_cents, 0) AS approved_cents,
    MAX(issued_invoice.total_cents - COALESCE(pst.posted_cents, 0) - COALESCE(apr.approved_cents, 0), 0) AS outstanding_cents
  FROM issued_invoice
  LEFT JOIN posted_sums AS pst ON pst.invoice_id = issued_invoice.invoice_id
  LEFT JOIN approved_sums AS apr ON apr.invoice_id = issued_invoice.invoice_id
)
SELECT
  ledger.id AS customer_id,
  ledger.name AS name,
  COALESCE(SUM(pv.total_cents), 0) AS invoice_total_cents,
  COALESCE(SUM(pv.posted_cents), 0) AS paid_cents,
  COALESCE(SUM(pv.approved_cents), 0) AS credit_cents,
  COALESCE(SUM(pv.outstanding_cents), 0) AS outstanding_cents
FROM customers AS ledger
LEFT JOIN per_invoice AS pv ON pv.customer_id = ledger.id
GROUP BY ledger.id, ledger.name
ORDER BY outstanding_cents DESC, customer_id ASC
