'use strict';

const assert = require('node:assert/strict');
const mod = require('./parse-csv.cjs');
const parseCsv = mod.parseCsv;

let passed = 0;
let failed = 0;

function run(label, fn) {
  try {
    fn();
    passed++;
    console.log('PASS ' + label);
  } catch (err) {
    failed++;
    console.log('FAIL ' + label);
    console.log('  ' + String(err && err.message || err).replace(/\r?\n/g, ' <newline> '));
  }
}

function expect(label, input, expected) {
  run(label, () => {
    const actual = parseCsv(input);
    assert.deepStrictEqual(actual, expected);
  });
}

function expectThrows(label, input, Ctor, messageRe) {
  run(label, () => {
    let thrown;
    try {
      parseCsv(input);
    } catch (err) {
      thrown = err;
    }
    assert.ok(thrown instanceof Ctor, 'expected a ' + Ctor.name + ' for ' + label);
    assert.strictEqual(thrown.name, Ctor.name);
    assert.match(thrown.message, messageRe);
  });
}

console.log('module exports: ' + JSON.stringify(Object.keys(mod)));
run('exports parseCsv as a function', () => {
  assert.deepStrictEqual(Object.keys(mod), ['parseCsv']);
  assert.strictEqual(typeof parseCsv, 'function');
});

// --- empty input ---
expect('empty input', '', []);

// --- plain rows, LF and CRLF ---
expect('single record', 'a,b,c', [['a', 'b', 'c']]);
expect('LF records', 'a,b\nc,d', [['a', 'b'], ['c', 'd']]);
expect('CRLF records', 'a,b\r\nc,d', [['a', 'b'], ['c', 'd']]);
expect('ragged records', 'a,b\nc', [['a', 'b'], ['c']]);

// --- trailing record ending must not add a phantom row ---
expect('trailing LF', 'a,b\n', [['a', 'b']]);
expect('trailing CRLF', 'a,b\r\n', [['a', 'b']]);
expect('all-CRLF with trailing ending', 'a\r\nb\r\n', [['a'], ['b']]);

// --- blank records stay as one empty field ---
expect('blank record in middle', 'a\n\nb', [['a'], [''], ['b']]);
expect('blank record before EOF', 'a\n\n', [['a'], ['']]);
expect('lone LF', '\n', [['']]);
expect('lone CRLF', '\r\n', [['']]);
expect('two CRLF endings', 'a,b\r\n\r\n', [['a', 'b'], ['']]);

// --- empty fields ---
expect('all empty fields', ',,', [['', '', '']]);
expect('empty around value', ',a,', [['', 'a', '']]);
expect('empty between values', 'a,,b', [['a', '', 'b']]);

// --- fully quoted fields ---
expect('quoted values', '"a","b"', [['a', 'b']]);
expect('quoted empty field', '""', [['']]);
expect('two quoted empty fields', '"",""', [['', '']]);
expect('quoted delimiter', '"a,b",c', [['a,b', 'c']]);

// --- doubled double-quotes ---
expect('doubled quotes', '"he said ""hi"""', [['he said "hi"']]);
expect('single literal quote', '""""', [['"']]);
expect('leading doubled quote', '"""x"', [['"x']]);

// --- embedded newlines inside quoted fields ---
expect('embedded LF', '"a\nb",c', [['a\nb', 'c']]);
expect('embedded CRLF preserved', '"a\r\nb",c', [['a\r\nb', 'c']]);
expect('embedded record endings count as one row', '"1\n2\n3",z', [['1\n2\n3', 'z']]);

// --- whitespace preserved ---
expect('unquoted whitespace kept', ' a , b ', [[' a ', ' b ']]);
expect('quoted whitespace kept', '"  x  ","  y"', [['  x  ', '  y']]);
expect('tabs kept', '\ta\t,b', [['\ta\t', 'b']]);

// --- Unicode ---
expect('unicode astral + latin', 'é,😀,ß', [['é', '😀', 'ß']]);
expect('unicode arabic + CRLF', 'مرhaba,world\r\nx,ي', [['مرhaba', 'world'], ['x', 'ي']]);
expect('unicode inside quotes with newline', '"مر\nhaba",😀', [['مر\nhaba', '😀']]);

// --- combined document ---
expect(
  'combined document',
  'name,notes\r\n"Doe, John","line1\nline2"\r\n,""\n"he said ""hi""",tail\n',
  [
    ['name', 'notes'],
    ['Doe, John', 'line1\nline2'],
    ['', ''],
    ['he said "hi"', 'tail'],
  ]
);

// --- non-string input -> TypeError ---
for (const bad of [42, 3.5, true, null, undefined, NaN, ['a,b'], { a: 1 }, new String('a,b')]) {
  const label = 'TypeError for ' + (bad === null ? 'null' : bad === undefined ? 'undefined' : bad === NaN ? 'NaN' : 'non-string');
  expectThrows(label, bad, TypeError, /must be a string/);
}

// --- malformed input -> SyntaxError ---
expectThrows('unclosed quoted field', '"a', SyntaxError, /unclosed quoted field/);
expectThrows('unclosed quoted field with newline', '"a\nb', SyntaxError, /unclosed quoted field/);
expectThrows('unclosed quote at EOF', 'a,"', SyntaxError, /unclosed quoted field/);
expectThrows('quote inside unquoted field', 'a"b', SyntaxError, /quote inside unquoted field/);
expectThrows('quote inside unquoted field after delimiter', 'a,b"c', SyntaxError, /quote inside unquoted field/);
expectThrows('quote inside unquoted field not at start', 'ab"c,d', SyntaxError, /quote inside unquoted field/);
expectThrows('text after closing quote', '"a"x', SyntaxError, /after closing quote/);
expectThrows('space after closing quote', '"a" ,b', SyntaxError, /after closing quote/);
expectThrows('empty quoted then text', '""x', SyntaxError, /after closing quote/);
expectThrows('text after closing quote before LF', '"a"b\nc', SyntaxError, /after closing quote/);

console.log('\npassed=' + passed + ' failed=' + failed);
if (failed > 0) {
  process.exitCode = 1;
}
