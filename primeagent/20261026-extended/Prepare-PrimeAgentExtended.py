"""Prepare new inputs and freeze the task contract before any agent request."""
import hashlib
import json
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parent
portal = root.parent
config = json.loads((portal / 'portal.config.json').read_text(encoding='utf-8-sig'))
stamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
directory = root / 'primeagent-extended' / stamp
workspace = Path(config['agentWorkspace']) / ('primeagent-extended-' + stamp)
directory.mkdir(parents=True, exist_ok=False)
for task in ['repair', 'sql', 'sudoku', 'evidence']:
    (workspace / task).mkdir(parents=True, exist_ok=False)

(workspace / 'repair/settlement.py').write_text('''"""Invoice settlement: currently mishandles decimal rounding and validates nothing."""
def settle_invoice(items, tax_percent='5', discount='0'):
    amounts = [round(float(row['unit_price']) * row['quantity'], 2) for row in items]
    subtotal = sum(amounts)
    tax = round(subtotal * float(tax_percent) / 100, 2)
    return {'line_totals': amounts, 'subtotal': subtotal, 'discount': discount,
            'tax': tax, 'total': subtotal + tax - float(discount)}
''', encoding='utf-8', newline='\n')
schema = '''CREATE TABLE customers(id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE invoices(id INTEGER PRIMARY KEY, customer_id INTEGER, total_cents INTEGER, status TEXT);
CREATE TABLE payments(id INTEGER PRIMARY KEY, invoice_id INTEGER, amount_cents INTEGER, status TEXT);
CREATE TABLE credits(id INTEGER PRIMARY KEY, invoice_id INTEGER, amount_cents INTEGER, status TEXT);'''
data = {
 'customers': [(1, 'مؤسسة المنارة'), (2, 'Northwind'), (3, 'No invoices'), (4, 'Overpaid')],
 'invoices': [(10,1,10000,'issued'),(11,1,20000,'issued'),(12,1,999999,'cancelled'),(20,2,5000,'issued'),(40,4,1000,'issued'),(41,4,2000,'issued')],
 'payments': [(1,10,1000,'posted'),(2,10,2000,'posted'),(3,11,5000,'posted'),(4,12,999999,'posted'),(5,10,7000,'pending'),(6,40,5000,'posted')],
 'credits': [(1,10,500,'approved'),(2,10,700,'approved'),(3,11,1000,'pending'),(4,20,500,'approved'),(5,12,6000,'approved')]
}
database = sqlite3.connect(workspace / 'sql/accounts.db')
database.executescript(schema)
for table, rows in data.items():
    database.executemany('INSERT INTO '+table+' VALUES ('+','.join('?' for _ in rows[0])+')', rows)
database.commit(); database.close()
(workspace / 'sql/schema.sql').write_text(schema, encoding='utf-8', newline='\n')
(directory / 'sql-fixture.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8', newline='\n')

puzzle = '530070000600195000098000060800060003400803001700020006060000280000419005000080079'
(workspace / 'sudoku/puzzle.txt').write_text(puzzle, encoding='utf-8')

def docx(filename, lines):
    paragraph = lambda text: '<w:p><w:r><w:t xml:space="preserve">'+escape(text)+'</w:t></w:r></w:p>'
    with ZipFile(workspace / 'evidence' / filename, 'w', ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
        z.writestr('_rels/.rels', '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        z.writestr('word/document.xml', '<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'+''.join(map(paragraph,lines))+'<w:sectPr/></w:body></w:document>')

docx('01-approved.docx', ['مشروع: واحة المعرفة','المورد: شركة النور','التاريخ: 2026-01-31','الحالة: معتمد','العملة: AED','الخدمات: 1250.25','المعدات: 749.75','المجموع: 2000.00'])
docx('02-approved.docx', ['مشروع: واحة المعرفة','المورد: شركة النور','التاريخ: 2026-02-28','الحالة: معتمد','العملة: AED','الخدمات: 1500.75','المعدات: 999.25','المجموع: 2500.00'])
docx('03-draft.docx', ['مشروع: واحة المعرفة','المورد: شركة النور','التاريخ: 2026-03-31','الحالة: مسودة غير معتمدة','العملة: AED','الخدمات: 900000.00','المعدات: 100000.00','المجموع: 1000000.00','هذه مسودة؛ لا تستخدم قيمها في التقرير المعتمد.'])

boundary = ' Work only in this task directory. Do not delegate, use network, change global settings, inspect other projects, or access the benchmark grader. Preserve source fixtures. Use the existing local tools and runtime.'
prompts = {
'repair': f'''PrimeAgent benchmark: repair the existing Python settlement module in {workspace / 'repair'}. Keep the public settle_invoice(items, tax_percent='5', discount='0') signature. Each item has quantity (positive int, excluding bool) and unit_price (nonnegative finite decimal string). tax_percent is a finite decimal string from 0 through 100; discount is a nonnegative finite decimal string. Empty items is allowed. Reject invalid inputs with ValueError. Use exact Decimal arithmetic: round each line quantity*price HALF_UP to cents, sum rounded lines, round discount HALF_UP to cents, reject discount above subtotal, and compute HALF_UP tax on (subtotal-discount). Return ONLY line_totals (list) and subtotal, discount, tax, total, with all monetary values formatted as two-decimal strings. Do not mutate items. Write your own regression tests, actually execute them with Python, and fix your failures. Explain the original bug and report actual test results.''' + boundary,
'sql': f'''PrimeAgent benchmark in {workspace / 'sql'}: inspect schema.sql and accounts.db. Write report.sql as one read-only SQLite SELECT (WITH allowed). Return EVERY customer, including those with no issued invoices, with these exact columns: customer_id, name, invoice_total_cents, paid_cents, credit_cents, outstanding_cents. Include only issued invoices; payments must be posted and credits approved. Do not multiply amounts when one invoice has multiple payments and credits. Outstanding is SUM over issued invoices of MAX(invoice total - its posted payments - its approved credits, 0), so an overpayment never cancels another invoice's debt. All amount columns must be integer cents, using 0 where absent. Sort outstanding_cents DESC then customer_id ASC. Execute it against accounts.db using Python sqlite3, save the actual row dictionaries as result.json, and write/run a small verification script. Do not modify the database.''' + boundary,
'sudoku': f'''PrimeAgent benchmark in {workspace / 'sudoku'}: build a playable self-contained sudoku.html without dependencies. Use puzzle.txt as the fixed starting puzzle (row-major 81 digits, 0 means empty). Render 81 input cells with data-row and data-col attributes, zero-based; lock given digits. Support typing 1-9 and clearing cells, and reject other input. Buttons with exact visible names: Check, Reset, Solve. A visible status element must have role="status". Check must distinguish a complete valid solution from incomplete or conflicting entries; an incomplete puzzle must NEVER report success. Reset restores precisely the given puzzle. Solve must compute a valid solution, preserve givens, and fill all cells. Support ArrowRight/ArrowLeft/ArrowDown/ArrowUp focus navigation within the 9x9 grid. Make it usable at phone width without horizontal overflow. Actually run meaningful checks on your generated game, using an available browser tool or an executable JS test harness. Register sudoku.html as a native artifact so the user can Download it. Report only actual outcomes.''' + boundary,
'evidence': f'''PrimeAgent benchmark in {workspace / 'evidence'}: read all three source DOCX reports with the connected document MCP tools. Choose the most recent APPROVED report by its document date, not the most recent filename/date regardless of status; compare it with the previous approved report. Use the connected math tool to independently check both totals, the change, and percent increase. Write result.json with EXACTLY: project, supplier, currency, currentDate, previousDate, currentSource, previousSource, excludedSources (filename list), currentTotal, previousTotal, delta, percentIncrease. Preserve exact Arabic project/supplier; amounts are JSON numbers. In the final answer cite each source filename and explain why the draft was excluded. Do not invent evidence or silently combine draft and approved amounts.''' + boundary,
}
plan = {'createdAtUtc':datetime.now(timezone.utc).isoformat(),'type':'PrimeAgent extended custom functional evaluation, not a standardized leaderboard','directory':str(directory),'workspace':str(workspace),'tasks':list(prompts),'downloads':{'sudoku':'.html'},'sampling':'Existing selected model and defaults unchanged','speedBenchmark':False,'retries':'One initial agent turn per task; self-correction within that turn retained; no grader feedback or external repair','rubric':{'repair':'Independent Decimal edge/invalid-input/nonmutation tests plus actual agent test execution','sql':'Read-only data preserved, correct rows on source and unseen join/overpayment/status fixtures','sudoku':'Actual browser typing, locking, checks, reset, solving, arrows, phone layout and downloadable byte equality','evidence':'Read all DOCX files, invoke exact math, preserve Arabic, choose approved evidence and exact totals'},'prompts':prompts}
for task in ['repair','sql','sudoku','evidence']:
    shutil.copytree(workspace/task,directory/'inputs'/task)
for name in ['Grade-PrimeAgentExtended.py','Grade-PrimeAgentSudoku.cjs']:
    source=root/name
    if not source.exists(): raise RuntimeError('Create the graders before freezing the benchmark.')
    shutil.copy2(source,directory/name)
plan['frozenGraderSha256']={name:hashlib.sha256((directory/name).read_bytes()).hexdigest() for name in ['Grade-PrimeAgentExtended.py','Grade-PrimeAgentSudoku.cjs']}
(directory/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8',newline='\n')
(root/'primeagent-extended/latest.txt').write_text(str(directory),encoding='utf-8')
print(json.dumps({'directory':str(directory),'workspace':str(workspace)}))
