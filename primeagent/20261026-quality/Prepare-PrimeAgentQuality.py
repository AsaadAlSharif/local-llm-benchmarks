"""Create fresh public inputs and a predeclared functional-test rubric."""
import json
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from xml.sax.saxutils import escape

root = Path(__file__).resolve().parent
portal = root.parent
config = json.loads((portal / 'portal.config.json').read_text(encoding='utf-8-sig'))
stamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
directory = root / 'primeagent-quality' / stamp
workspace = Path(config['agentWorkspace']) / ('primeagent-quality-' + stamp)
directory.mkdir(parents=True, exist_ok=False)
for name in ['coding', 'documents', 'presentation']:
    (workspace / name).mkdir(parents=True, exist_ok=False)
paragraph = lambda text: '<w:p><w:r><w:t xml:space="preserve">' + escape(text) + '</w:t></w:r></w:p>'
body = ''.join(paragraph(text) for text in ['PrimeAgent local evaluation invoice', 'Invoice ID: PA-2026-042', 'Supplier: مؤسسة المنارة', 'Currency: AED'])
rows = [('Service', 'Quantity', 'Unit price (AED)'), ('تحليل البيانات', '3', '124.50'), ('إعداد العرض', '2', '80.00')]
body += '<w:tbl>' + ''.join('<w:tr>' + ''.join('<w:tc>' + paragraph(value) + '</w:tc>' for value in row) + '</w:tr>' for row in rows) + '</w:tbl>'
body += paragraph('VAT: 5% of the subtotal. Round VAT to two decimal places using round-half-up. Total = subtotal + rounded VAT.')
with ZipFile(workspace / 'documents' / 'source-invoice.docx', 'w', ZIP_DEFLATED) as document:
    document.writestr('[Content_Types].xml', '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
    document.writestr('_rels/.rels', '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
    document.writestr('word/document.xml', '<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>' + body + '<w:sectPr/></w:body></w:document>')
fixture = {'invoiceId': 'PA-2026-042', 'supplier': 'مؤسسة المنارة', 'currency': 'AED', 'lineTotals': [373.50, 160.00], 'subtotal': 533.50, 'vat': 26.68, 'total': 560.18}
(directory / 'expected-invoice.json').write_text(json.dumps(fixture, ensure_ascii=False, indent=2), encoding='utf-8')
prompts = {
 'coding': f'''PrimeAgent independent functional test. Work only in {workspace / 'coding'}. Implement parse-csv.cjs exporting {{ parseCsv }} and write test.cjs with node:assert/strict. parseCsv(text) returns an array of rows (each an array of strings). Support commas, LF and CRLF record endings, fully quoted fields, doubled double-quotes, embedded newlines inside quoted fields, Unicode, and empty fields. Preserve field whitespace. Empty input returns []. A final record ending must not create a phantom extra row; actual blank records remain single empty fields. Reject non-string input with TypeError, and reject unclosed quoted fields, quotes appearing within unquoted fields, and characters following a closing quote before a delimiter/record ending with SyntaxError. Use only Node standard libraries. Actually execute your test.cjs with node.exe and fix your own failures. Do not delegate, change settings, inspect other projects or use network. Do not write outside the requested directory. Report PRIMEAGENT_CSV_DONE and actual test outcomes only after running them.''',
 'documents': f'''PrimeAgent local Arabic document/tool functional test. Read {workspace / 'documents' / 'source-invoice.docx'} using the connected document-reading MCP tool. Discover and invoke the connected exact-math MCP calculator to compute its line totals, subtotal, VAT and final total. Follow the invoice's stated rounding rule. Write {workspace / 'documents' / 'invoice-result.json'} with exactly these fields: invoiceId, supplier, currency, lineTotals (array in source order), subtotal, vat, total. Keep the supplier's exact Arabic text and use JSON numbers for amounts. Do not use shell or external network, delegate, read unrelated files or change settings. Report PRIMEAGENT_INVOICE_DONE with the actual values after reading the document, calling the calculator and writing the JSON.''',
 'presentation': f'''PrimeAgent local artifact functional test. Read the existing {workspace / 'documents' / 'invoice-result.json'}. If it is absent, report blocked without inventing values. Using the connected presentation MCP tool, create exactly TWO slides. First title: "PrimeAgent — Asaad AlSharif". First slide includes the invoice ID, exact Arabic supplier and both line totals. Second title: "Verified totals". Second slide includes subtotal, VAT, total and currency exactly as recorded in the JSON. Set output_name to "primeagent-quality-{stamp}". Register the resulting PowerPoint with the native artifact tool so the user sees a working Download button. Do not use shell or network, delegate, change settings or modify the source JSON. Report PRIMEAGENT_PRESENTATION_DONE and the downloadable artifact after actual tool success.'''
}
plan = {'createdAtUtc': datetime.now(timezone.utc).isoformat(), 'type': 'custom functional evaluation; not a standardized leaderboard benchmark', 'directory': str(directory), 'workspace': str(workspace), 'tasks': list(prompts), 'sampling': 'existing PrimeAgent/model settings unchanged', 'speedBenchmark': False, 'retries': 'no quality retries; original attempts retained', 'rubric': {'coding': 'Independent parser examples, malformed inputs and serialized CSV round-trip properties; agent must write and execute its own tests.', 'documents': 'Actual document-reading and math MCP invocations, exact Arabic extraction and independently checked monetary values.', 'presentation': 'Actual presentation MCP invocation, native artifact registration, browser Download, two-slide PPTX inspection and source-value agreement.'}, 'prompts': prompts}
(directory / 'plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding='utf-8')
(root / 'primeagent-quality' / 'latest.txt').write_text(str(directory), encoding='utf-8')
print(json.dumps({'directory': str(directory), 'workspace': str(workspace)}, ensure_ascii=True))
