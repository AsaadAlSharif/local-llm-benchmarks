"""Run report.sql against accounts.db (SQLite read-only) and save result.json."""
import json
import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = HERE / "accounts.db"
SQL = (HERE / "report.sql").read_text(encoding="utf-8")

code = "\n".join(line.split("--", 1)[0] for line in SQL.splitlines())
body = code.upper()
for forbidden in ("INSERT", "UPDATE", "DELETE", "REPLACE", "CREATE ", "DROP", "ALTER", "PRAGMA", "ATTACH"):
    if forbidden in body:
        raise SystemExit("refusing: report.sql is not read-only")
if not body.lstrip().startswith(("WITH", "SELECT")):
    raise SystemExit("refusing: report.sql is not a SELECT")

con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
cur = con.cursor()
cur.execute(SQL)
cols = [d[0] for d in cur.description]
rows = [dict(zip(cols, row)) for row in cur.fetchall()]
con.close()

(HERE / "result.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

print("sqlite version:", sqlite3.sqlite_version)
print("columns:", cols)
for r in rows:
    print(r)
print("rows:", len(rows))
