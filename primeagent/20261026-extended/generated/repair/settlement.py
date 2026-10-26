"""Invoice settlement with exact Decimal money arithmetic and strict validation."""

from collections.abc import Mapping
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

_CENT = Decimal('0.01')
_ZERO = Decimal('0')
_HUNDRED = Decimal('100')


def _parse_decimal(value, label):
    if not isinstance(value, str):
        raise ValueError(f'{label} must be a decimal string')
    try:
        parsed = Decimal(value)
    except InvalidOperation:
        raise ValueError(f'{label} must be a finite decimal string') from None
    if not parsed.is_finite():
        raise ValueError(f'{label} must be a finite decimal string')
    return parsed


def _round_cents(value):
    cents = value.quantize(_CENT, rounding=ROUND_HALF_UP)
    if cents == 0:
        cents = cents.copy_abs()
    return cents


def _format_cents(value):
    return f'{_round_cents(value):.2f}'


def _get_field(row, label):
    if not isinstance(row, Mapping):
        raise ValueError(f'{label} must be a mapping with quantity and unit_price')
    try:
        return row['quantity'], row['unit_price']
    except KeyError:
        raise ValueError(f'{label} must define quantity and unit_price') from None


def _quantity(value, label):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f'{label} quantity must be a positive integer')
    if value <= 0:
        raise ValueError(f'{label} quantity must be a positive integer')
    return value


def _unit_price(value, label):
    price = _parse_decimal(value, f'{label} unit_price')
    if price < 0:
        raise ValueError(f'{label} unit_price must be nonnegative')
    return price


def settle_invoice(items, tax_percent='5', discount='0'):
    if not isinstance(items, (list, tuple)):
        raise ValueError('items must be a list of invoice line mappings')

    tax_rate = _parse_decimal(tax_percent, 'tax_percent')
    if tax_rate < 0 or tax_rate > _HUNDRED:
        raise ValueError('tax_percent must be between 0 and 100')

    discount_value = _parse_decimal(discount, 'discount')
    if discount_value < 0:
        raise ValueError('discount must be nonnegative')

    line_totals = []
    subtotal = _ZERO
    for index, row in enumerate(items):
        quantity, raw_price = _get_field(row, f'item {index}')
        price = _unit_price(raw_price, f'item {index}')
        count = _quantity(quantity, f'item {index}')
        line_total = _round_cents(price * count)
        line_totals.append(line_total)
        subtotal += line_total

    discount_value = _round_cents(discount_value)
    if discount_value > subtotal:
        raise ValueError('discount must not exceed the subtotal')

    net = subtotal - discount_value
    tax = _round_cents(net * tax_rate / _HUNDRED)
    total = net + tax

    return {
        'line_totals': [_format_cents(value) for value in line_totals],
        'subtotal': _format_cents(subtotal),
        'discount': _format_cents(discount_value),
        'tax': _format_cents(tax),
        'total': _format_cents(total),
    }
