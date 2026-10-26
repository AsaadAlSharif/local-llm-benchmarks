"""Invoice settlement: currently mishandles decimal rounding and validates nothing."""
def settle_invoice(items, tax_percent='5', discount='0'):
    amounts = [round(float(row['unit_price']) * row['quantity'], 2) for row in items]
    subtotal = sum(amounts)
    tax = round(subtotal * float(tax_percent) / 100, 2)
    return {'line_totals': amounts, 'subtotal': subtotal, 'discount': discount,
            'tax': tax, 'total': subtotal + tax - float(discount)}
