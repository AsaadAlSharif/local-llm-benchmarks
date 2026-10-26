// Independent logic check: fixture vs embedded puzzle, structure, and the puzzle's own solution.
// Written independently of sudoku.html's solver so it cannot inherit its bugs.
import fs from 'node:fs';
const dir = import.meta.dirname;

const fixture = fs.readFileSync(dir + '/puzzle.txt', 'utf8').replace(/[^0-9]/g, '');
const html = fs.readFileSync(dir + '/sudoku.html', 'utf8');

const results = [];
function check(name, ok, detail) { results.push({ name, ok: !!ok, detail: String(detail) }); }

const m = /data-puzzle="([0-9]{81})"/.exec(html);
check('embedded puzzle present', m, m ? '' : 'no 81-digit data-puzzle attribute');
check('embedded puzzle === puzzle.txt', m && m[1] === fixture, m ? m[1] + ' vs ' + fixture : 'n/a');

// Structure
const inputTags = html.match(/<input\b[^>]*>/g) || [];
const gridTags = inputTags.filter(t => t.includes('data-row=') && t.includes('data-col='));
check('81 grid inputs', gridTags.length === 81, gridTags.length);
let attrOk = true;
for (let i = 0; i < gridTags.length; i++) {
  const r = /data-row="(\d+)"/.exec(gridTags[i]);
  const c = /data-col="(\d+)"/.exec(gridTags[i]);
  const idx = /data-index="(\d+)"/.exec(gridTags[i]);
  const g = /data-given="(true|false)"/.exec(gridTags[i]);
  const v = /value="([0-9]?)"/.exec(gridTags[i]);
  if (!r || !c || !idx || !g || !v) { attrOk = false; break; }
  if (+r[1] * 9 + +c[1] !== +idx[1]) { attrOk = false; break; }
  const wantGiven = fixture[+idx[1]] !== '0';
  if ((g[1] === 'true') !== wantGiven) { attrOk = false; break; }
  if (v[1] !== (wantGiven ? fixture[+idx[1]] : '')) { attrOk = false; break; }
}
check('data-row/data-col/data-given/value correct for all cells', attrOk, attrOk ? 'rows/cols 0..8 zero-based' : 'mismatch');
check('role="status" present exactly once', (html.match(/role="status"/g) || []).length === 1, (html.match(/role="status"/g) || []).length);
for (const name of ['Check', 'Reset', 'Solve']) {
  const re = new RegExp('<button[^>]*>' + name + '</button>');
  check('button with exact visible name ' + name, re.test(html), '');
}
check('no external subresource refs', !/<script[^>]+\bsrc=|<link[^>]+\bhref=/.test(html), '');

// Independent solver (different style from the page's): plain backtracking with bitmask units.
const digits = fixture.split('').map(d => (d === '0' ? 0 : +d));
const UNITS = [];
for (let band = 0; band < 3; band++) {
  for (let stack = 0; stack < 3; stack++) {
    const box = [];
    for (let dr = 0; dr < 3; dr++) for (let dc = 0; dc < 3; dc++) box.push((band * 3 + dr) * 9 + stack * 3 + dc);
    UNITS.push(box);
  }
}
const ALL = [];
for (let r = 0; r < 9; r++) ALL.push(Array.from({length: 9}, (_, k) => r * 9 + k));
for (let c = 0; c < 9; c++) ALL.push(Array.from({length: 9}, (_, k) => k * 9 + c));
for (let b = 0; b < 9; b++) ALL.push(UNITS[b]);

const cellUnits = Array.from({length: 81}, (_, i) => ALL.filter(u => u.includes(i)));
let givenConflict = 0;
for (const u of ALL) {
  const seen = new Set();
  for (const i of u) { const d = digits[i]; if (d && seen.has(d)) givenConflict++; if (d) seen.add(d); }
}
check('givens do not conflict', givenConflict === 0, givenConflict);

let solutionFound = null;
function countSolve(grid, limit) {
  let count = 0;
  const blanks = [];
  for (let i = 0; i < 81; i++) if (!grid[i]) blanks.push(i);
  function walk(k) {
    if (count >= limit) return;
    if (k === blanks.length) { count++; if (count === 1) solutionFound = grid.slice(); return; }
    const i = blanks[k];
    for (let d = 1; d <= 9; d++) {
      let ok = true;
      for (const u of cellUnits[i]) { if (u.some(j => grid[j] === d)) { ok = false; break; } }
      if (!ok) continue;
      grid[i] = d;
      walk(k + 1);
      grid[i] = 0;
      if (count >= limit) return;
    }
  }
  walk(0);
  return count;
}
const n = countSolve(digits.slice(), 2);
check('puzzle has at least one solution', n >= 1, n);
check('solution is unique', n === 1, n);

const sol = solutionFound;
function validSolution(g) {
  for (const u of ALL) {
    const s = new Set(u.map(i => g[i]));
    if (s.size !== 9) return false;
  }
  return true;
}
check('unique solution is valid', validSolution(sol), '');
check('solution preserves givens', digits.every((d, i) => !d || d === sol[i]), '');

fs.writeFileSync(dir + '/logic-report.json', JSON.stringify({ fixture, embedded: m && m[1], solution: sol.join(''), results }, null, 2), 'utf8');
const fails = results.filter(r => !r.ok);
process.stdout.write(results.map(r => (r.ok ? 'PASS ' : 'FAIL ') + r.name + (r.ok ? '' : ' :: ' + r.detail)).join('\n') + '\n' + (fails.length ? 'FAILURES: ' + fails.length + '\n' : 'ALL PASS\n'));
if (fails.length) process.exit(1);
