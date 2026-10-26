'use strict';

const COMMA = 0x2c;
const QUOTE = 0x22;
const LF = 0x0a;
const CR = 0x0d;

function parseCsv(text) {
  if (typeof text !== 'string') {
    throw new TypeError('parseCsv: input must be a string, got ' + typeof text);
  }

  const rows = [];
  if (text.length === 0) {
    return rows;
  }

  const n = text.length;
  let i = 0;
  let row = [];

  for (;;) {
    let value;

    if (text.charCodeAt(i) === QUOTE) {
      const quoteStart = i;
      i++;
      let from = i;
      const parts = [];
      let closed = false;

      while (i < n) {
        const code = text.charCodeAt(i);
        if (code !== QUOTE) {
          i++;
          continue;
        }
        if (i + 1 < n && text.charCodeAt(i + 1) === QUOTE) {
          parts.push(text.slice(from, i));
          parts.push('"');
          i += 2;
          from = i;
          continue;
        }
        parts.push(text.slice(from, i));
        closed = true;
        i++;
        break;
      }

      if (!closed) {
        throw new SyntaxError('parseCsv: unclosed quoted field at index ' + quoteStart);
      }

      if (i < n) {
        const after = text.charCodeAt(i);
        if (after !== COMMA && after !== LF && after !== CR) {
          throw new SyntaxError(
            'parseCsv: unexpected character after closing quote at index ' + i
          );
        }
      }

      value = parts.length === 1 ? parts[0] : parts.join('');
    } else {
      const start = i;
      while (i < n) {
        const code = text.charCodeAt(i);
        if (code === COMMA || code === LF || code === CR) {
          break;
        }
        if (code === QUOTE) {
          throw new SyntaxError('parseCsv: quote inside unquoted field at index ' + i);
        }
        i++;
      }
      value = text.slice(start, i);
    }

    if (i === n) {
      row.push(value);
      rows.push(row);
      return rows;
    }

    const code = text.charCodeAt(i);
    if (code === COMMA) {
      row.push(value);
      i++;
      continue;
    }

    row.push(value);
    rows.push(row);
    i += code === CR && i + 1 < n && text.charCodeAt(i + 1) === LF ? 2 : 1;
    if (i === n) {
      return rows;
    }
    row = [];
  }
}

exports.parseCsv = parseCsv;
