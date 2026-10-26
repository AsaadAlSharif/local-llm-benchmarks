const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const dir = fs.readFileSync(path.join(__dirname, 'primeagent-quality/latest.txt'), 'utf8').trim();
const plan = JSON.parse(fs.readFileSync(path.join(dir, 'plan.json'), 'utf8'));
const file = path.join(plan.workspace, 'coding/parse-csv.cjs');
const { parseCsv } = require(file);
const checks = [];
function check(name, fn) {
  try { fn(); checks.push({name,passed:true}); }
  catch (error) { checks.push({name,passed:false,error:error.message}); }
}
for (const [name, input, expected] of [
  ['empty document', '', []], ['blank LF record', '\n', [['']]],
  ['two blank records', '\n\n', [[''],['']]], ['trailing comma','a,',[['a','']]],
  ['empty values',',,',[['','','']]], ['single quoted empty','""',[['']]],
  ['escaped quote','""""',[['"']]], ['quoted commas','"a,b",c',[['a,b','c']]],
  ['LF rows','a,b\nc,d',[['a','b'],['c','d']]],
  ['CRLF ending','a,b\r\nc,d\r\n',[['a','b'],['c','d']]],
  ['blank final record','a\n\n',[['a'],['']]],
  ['multiline field','"a\r\nb",c',[['a\r\nb','c']]],
  ['whitespace preserved',' a ," b "',[[' a ',' b ']]],
  ['Arabic and emoji','مرحبا,😀',[['مرحبا','😀']]],
  ['ragged rows','a\nb,c',[['a'],['b','c']]]
]) check(name, () => assert.deepEqual(parseCsv(input), expected));
for (const [index,value] of [null,undefined,42,NaN,Infinity,{},[],true,1n,new String('a')].entries())
  check('non-string ' + index, () => assert.throws(() => parseCsv(value), TypeError));
for (const [index,value] of ['"','"a','a"b','"a"x','"a" ,b','a,"b','a,b"c','""x','"a"b\nc'].entries())
  check('malformed ' + index, () => assert.throws(() => parseCsv(value), SyntaxError));
let seed=0x6391a2;
const next=limit => {seed=(Math.imul(seed,1664525)+1013904223)>>>0; return seed%limit;};
const fields=['','plain',' a ','x,y','a"b','line\nnext','line\r\nnext','مؤسسة المنارة','😀','\t'];
for (let i=0;i<512;i++) {
  const rows=Array.from({length:1+next(4)},()=>Array.from({length:1+next(5)},()=>fields[next(fields.length)]));
  const ending=i%2?'\r\n':'\n';
  const encoded=rows.map(row=>row.map(value => '"'+value.replaceAll('"','""')+'"').join(',')).join(ending)+(i%3===0?ending:'');
  check('round-trip '+i,()=>assert.deepEqual(parseCsv(encoded),rows));
}
const result={checkedAtUtc:new Date().toISOString(),source:file,kind:'independent examples and CSV serialization round-trip properties',checks:checks.length,passed:checks.filter(row=>row.passed).length,failed:checks.filter(row=>!row.passed),details:checks};
fs.writeFileSync(path.join(dir,'independent-csv-verification.json'),JSON.stringify(result,null,2));
console.log(JSON.stringify({checks:result.checks,passed:result.passed,failed:result.failed}));
if(result.failed.length)process.exitCode=1;
