// Serves sudoku.html over http://127.0.0.1:8731/ for the browser test pass (file:// is blocked by the browser tool).
import http from 'node:http';
import fs from 'node:fs';
const dir = import.meta.dirname;
const server = http.createServer((req, res) => {
  res.setHeader('content-type', 'text/html; charset=utf-8');
  res.end(fs.readFileSync(dir + '/sudoku.html', 'utf8'));
});
server.listen(8731, '127.0.0.1');
process.stdout.write('serving sudoku.html on http://127.0.0.1:8731/\n');
