"""Independent verification of result.json against accounts.db (pure Python recompute, no SQL aggregation)."""
import json
import sqlite3
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = HERE / "accounts.db"
rows = json.loads((HERE / "result.json").read_text(encoding="utf-8"))

COLS = ["customer_id", "name", "invoice_total_cents", "paid_cents", "credit_cents", "outstanding_cents"]
AMOUNT_COLS = COLS[2:]
fails = []


def check(label, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'} | {label} | {detail}")
    if not ok:
        fails.append(label)


con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
cur = con.cursor()
cur.execute("SELECT id, name FROM customers")
customers = {r[0]: r[1] for r in cur.fetchall()}
cur.execute("SELECT id, customer_id, total_cents, status FROM invoices")
invoices = [dict(zip(("id", "customer_id", "total_cents", "status"), r)) for r in cur.fetchall()]
cur.execute("SELECT id, invoice_id, amount_cents, status FROM payments")
payments = [dict(zip(("id", "invoice_id", "amount_cents", "status"), r)) for r in cur.fetchall()]
cur.execute("SELECT id, invoice_id, amount_cents, status FROM credits")
credits = [dict(zip(("id", "invoice_id", "amount_cents", "status"), r)) for r in cur.fetchall()]
con.close()

issued = {i["id"]: i for i in invoices if i["status"] == "issued"}
posted = defaultdict(int)
for p in payments:
    if p["status"] == "posted" and p["invoice_id"] in issued:
        posted[p["invoice_id"]] += p["amount_cents"]
approved = defaultdict(int)
for c in credits:
    if c["status"] == "approved" and c["invoice_id"] in issued:
        approved[c["invoice_id"]] += c["amount_cents"]

expected = {}
for cid, name in customers.items():
    total = paid = credit = outstanding = 0
    for iid, inv in issued.items():
        if inv["customer_id"] != cid:
            continue
        total += inv["total_cents"]
        paid += posted[iid]
        credit += approved[iid]
        outstanding += max(inv["total_cents"] - posted[iid] - approved[iid], 0)
    expected[cid] = {"customer_id": cid, "name": name, "invoice_total_cents": total,
                     "paid_cents": paid, "credit_cents": credit, "outstanding_cents": outstanding}

got = {r["customer_id"]: r for r in rows}

check("columns exact and ordered",
      all(list(r) == COLS for r in rows), f"{len(rows)} rows, keys={COLS}")
check("every customer returned incl. no-invoice customers",
      sorted(got) == sorted(customers), f"sql={sorted(got)} db={sorted(customers)}")
check("one row per customer (no join fan-out)",
      len(rows) == len(customers) == len(got), f"rows={len(rows)} customers={len(customers)}")
for r in rows:
    for col in AMOUNT_COLS:
        check(f"row {r['customer_id']} {col} is int cents", type(r[col]) is int, f"value={r[col]!r}")
check("amounts are integer cents, none negative, no NULL",
      all(type(r[col]) is int and r[col] >= 0 for r in rows for col in AMOUNT_COLS),
      f"min={min(r[col] for r in rows for col in AMOUNT_COLS)}")
for cid in sorted(customers):
    check(f"row {cid} matches independent Python recompute",
          all(got[cid][c] == expected[cid][c] for c in COLS),
          f"sql={{k: got[cid][k] for k in COLS}}")

i10, p10, c10 = issued[10], [p for p in payments if p["invoice_id"] == 10 and p["status"] == "posted"], [c for c in credits if c["invoice_id"] == 10 and c["status"] == "approved"]
check("multiplicity guard: inv 10 has 2 posted payments AND 2 approved credits",
      len(p10) == 2 and len(c10) == 2 and
      got[1]["paid_cents"] == posted[10] + posted[11] and posted[10] == sum(p["amount_cents"] for p in p10) and
      got[1]["credit_cents"] == sum(c["amount_cents"] for c in c10) and
      got[1]["invoice_total_cents"] == issued[10]["total_cents"] + issued[11]["total_cents"],
      f"inv10 payments={[p['amount_cents'] for p in p10]} credits={[c['amount_cents'] for c in c10]} -> "
      f"paid(1)={got[1]['paid_cents']} (=3000+5000, payments summed once not 2x2), credit(1)={got[1]['credit_cents']}, "
      f"total(1)={got[1]['invoice_total_cents']} (totals counted once, not 4x)")

canc = [i for i in invoices if i["status"] != "issued"]
check("only issued invoices: cancelled inv 12 (999999) excluded",
      got[1]["invoice_total_cents"] < sum(i["total_cents"] for i in invoices if i["customer_id"] == 1),
      f"sql total(1)={got[1]['invoice_total_cents']} vs all-status total={sum(i['total_cents'] for i in invoices if i['customer_id'] == 1)}")
check("posted payment 999999 on cancelled inv 12 excluded from paid_cents",
      got[1]["paid_cents"] == 8000,
      f"paid(1)={got[1]['paid_cents']}; including inv 12 would give {got[1]['paid_cents'] + 999999}")
check("approved credit 6000 on cancelled inv 12 excluded from credit_cents",
      got[1]["credit_cents"] == 1200,
      f"credit(1)={got[1]['credit_cents']}; including inv 12 would give {got[1]['credit_cents'] + 6000}")
check("pending payment 7000 on inv 10 excluded",
      got[1]["paid_cents"] == 3000 + 5000,
      f"paid(1)={got[1]['paid_cents']}")
check("pending credit 1000 on inv 11 excluded",
      got[1]["credit_cents"] == 1200,
      f"credit(1)={got[1]['credit_cents']}")
check("customer with no invoices -> all amount columns 0",
      all(got[3][c] == 0 for c in AMOUNT_COLS) and 3 in customers,
      f"customer 3 'No invoices' -> {[got[3][c] for c in AMOUNT_COLS]}")

o = [r["outstanding_cents"] for r in rows]
check("sort: outstanding_cents DESC", o == sorted(o, reverse=True), f"outstanding={o}")
check("sort tiebreak: customer_id ASC within equal outstanding",
      rows == sorted(rows, key=lambda r: (-r["outstanding_cents"], r["customer_id"])),
      f"order={[(r['outstanding_cents'], r['customer_id']) for r in rows]}")
check("overpayment clamped per invoice, debt not cross-cancelled (cust 4)",
      got[4]["outstanding_cents"] == 2000 and got[4]["paid_cents"] == 5000 and got[4]["invoice_total_cents"] == 3000,
      "inv40 total 1000 vs posted 5000 -> max(...,0)=0; inv41 total 2000 with no payments -> keeps its own 2000")

for col in AMOUNT_COLS:
    check(f"column total invariant: {col}",
          sum(r[col] for r in rows) == sum(expected[c][col] for c in expected),
          f"sql={sum(r[col] for r in rows)} py={sum(expected[c][col] for c in expected)}")

sql_text = (HERE / "report.sql").read_text(encoding="utf-8")

# The fixture has no tie in outstanding_cents, so ORDER BY's customer_id tiebreak is
# unexercised above. Prove it on an in-memory rebuild from the fixture rows plus one
# synthetic customer; accounts.db itself is never written to.
mem = sqlite3.connect(":memory:")
for line in (HERE / "schema.sql").read_text(encoding="utf-8").splitlines():
    if line.strip():
        mem.execute(line)
fixture_recs = {
    "customers": [{"id": cid, "name": nm} for cid, nm in customers.items()],
    "invoices": invoices,
    "payments": payments,
    "credits": credits,
}
for tbl, recs in fixture_recs.items():
    keys = list(recs[0])
    mem.execute(f"INSERT INTO {tbl} ({','.join(keys)}) VALUES " +
                ",".join(["(" + ",".join("?" * len(keys)) + ")"] * len(recs)),
                [v for row in recs for v in row.values()])
mem.execute("INSERT INTO customers (id, name) VALUES (0, 'Zero-tie test')")
cur_tie = mem.execute(sql_text)
tie_cols = [d[0] for d in cur_tie.description]
tie_rows = [dict(zip(tie_cols, r)) for r in cur_tie.fetchall()]
mem.close()

zero_tie = [(r["outstanding_cents"], r["customer_id"]) for r in tie_rows if r["outstanding_cents"] == 0]
check("ORDER BY tiebreak exercised (synthetic customer 0 ties outstanding 0 before customer 3)",
      zero_tie == sorted(zero_tie, key=lambda t: (t[0], t[1])) and (0, 0) in zero_tie and len(zero_tie) == 2,
      f"zero-outstanding pairs={zero_tie}")

import hashlib
import os
import time

st = os.stat(DB)
print(f"fixture accounts.db: size={st.st_size} sha256={hashlib.sha256(DB.read_bytes()).hexdigest()} "
      f"mtime={time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.st_mtime))}")
print("accounts.db opened only as file:...?mode=ro (SQLite read-only mount); tiebreak test ran on :memory: copy")

print("\nRESULT:", "ALL CHECKS PASS" if not fails else f"{len(fails)} FAILURES -> {fails}")
raise SystemExit(0 if not fails else 1)
