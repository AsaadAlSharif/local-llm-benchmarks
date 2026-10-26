"""Regression tests for settle_invoice."""

import copy
import unittest

import settlement
from decimal import Decimal

settle = settlement.settle_invoice


def assert_raises_value(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except ValueError:
        return
    raise AssertionError(f'expected ValueError, got no error (args={args!r})')


class TestRounding(unittest.TestCase):

    def test_half_up_line_total(self):
        # 1 * 1.005 -> float round() gives '1.0', Decimal HALF_UP gives 1.01
        out = settle([{'quantity': 1, 'unit_price': '1.005'}])
        self.assertEqual(out['line_totals'], ['1.01'])
        self.assertEqual(out['subtotal'], '1.01')

    def test_half_up_with_quantity(self):
        # 3 * 2.675 = 8.025 -> 8.03
        out = settle([{'quantity': 3, 'unit_price': '2.675'}])
        self.assertEqual(out['line_totals'], ['8.03'])
        self.assertEqual(out['subtotal'], '8.03')

    def test_exact_accumulation(self):
        out = settle([{'quantity': 1, 'unit_price': '0.1'}] * 3)
        self.assertEqual(out['line_totals'], ['0.10', '0.10', '0.10'])
        self.assertEqual(out['subtotal'], '0.30')

    def test_tax_half_up_tie(self):
        # 10.00 * 1.05 / 100 = 0.105 -> HALF_UP 0.11 (float round -> 0.1)
        out = settle([{'quantity': 1, 'unit_price': '10.00'}], tax_percent='1.05')
        self.assertEqual(out['tax'], '0.11')
        self.assertEqual(out['total'], '10.11')

    def test_discount_half_up(self):
        out = settle([{'quantity': 1, 'unit_price': '10.00'}], discount='1.999')
        self.assertEqual(out['discount'], '2.00')
        self.assertEqual(out['subtotal'], '10.00')


class TestTaxBase(unittest.TestCase):

    def test_tax_on_net(self):
        out = settle([{'quantity': 2, 'unit_price': '50.00'}], tax_percent='10', discount='10.00')
        self.assertEqual(out['line_totals'], ['100.00'])
        self.assertEqual(out['subtotal'], '100.00')
        self.assertEqual(out['discount'], '10.00')
        self.assertEqual(out['tax'], '9.00')
        self.assertEqual(out['total'], '99.00')

    def test_zero_tax(self):
        out = settle([{'quantity': 1, 'unit_price': '7.77'}], tax_percent='0')
        self.assertEqual(out['tax'], '0.00')
        self.assertEqual(out['total'], '7.77')

    def test_hundred_percent_tax(self):
        out = settle([{'quantity': 1, 'unit_price': '7.77'}], tax_percent='100')
        self.assertEqual(out['tax'], '7.77')
        self.assertEqual(out['total'], '15.54')

    def test_tax_percent_boundary(self):
        assert_raises_value(settle, [], tax_percent='100.001')
        assert_raises_value(settle, [], tax_percent='-0.001')
        assert_raises_value(settle, [], tax_percent='nan')
        assert_raises_value(settle, [], tax_percent='Infinity')
        assert_raises_value(settle, [], tax_percent='abc')
        assert_raises_value(settle, [], tax_percent=5)

    def test_discount_boundaries(self):
        assert_raises_value(settle, [{'quantity': 1, 'unit_price': '10.00'}], discount='-0.01')
        assert_raises_value(settle, [{'quantity': 1, 'unit_price': '10.00'}], discount='10.01')
        assert_raises_value(settle, [{'quantity': 1, 'unit_price': '10.00'}], discount='nan')
        assert_raises_value(settle, [{'quantity': 1, 'unit_price': '10.00'}], discount='Infinity')
        assert_raises_value(settle, [{'quantity': 1, 'unit_price': '10.00'}], discount=0)

    def test_discount_equal_subtotal(self):
        out = settle([{'quantity': 1, 'unit_price': '10.00'}], tax_percent='19.6', discount='10')
        self.assertEqual(out['discount'], '10.00')
        self.assertEqual(out['tax'], '0.00')
        self.assertEqual(out['total'], '0.00')


class TestValidation(unittest.TestCase):

    def test_quantity_rules(self):
        assert_raises_value(settle, [{'quantity': True, 'unit_price': '1.00'}])
        assert_raises_value(settle, [{'quantity': False, 'unit_price': '1.00'}])
        assert_raises_value(settle, [{'quantity': 0, 'unit_price': '1.00'}])
        assert_raises_value(settle, [{'quantity': -1, 'unit_price': '1.00'}])
        assert_raises_value(settle, [{'quantity': 2.0, 'unit_price': '1.00'}])
        assert_raises_value(settle, [{'quantity': '2', 'unit_price': '1.00'}])
        assert_raises_value(settle, [{'quantity': Decimal('2'), 'unit_price': '1.00'}])

    def test_unit_price_rules(self):
        assert_raises_value(settle, [{'quantity': 1, 'unit_price': '-0.01'}])
        assert_raises_value(settle, [{'quantity': 1, 'unit_price': 'nan'}])
        assert_raises_value(settle, [{'quantity': 1, 'unit_price': 'Infinity'}])
        assert_raises_value(settle, [{'quantity': 1, 'unit_price': ''}])
        assert_raises_value(settle, [{'quantity': 1, 'unit_price': '1.0.0'}])
        assert_raises_value(settle, [{'quantity': 1, 'unit_price': 1.5}])
        assert_raises_value(settle, [{'quantity': 1, 'unit_price': 15}])

    def test_missing_keys(self):
        assert_raises_value(settle, [{'quantity': 1}])
        assert_raises_value(settle, [{'unit_price': '1.00'}])

    def test_bad_container(self):
        assert_raises_value(settle, 'nope')
        assert_raises_value(settle, {'quantity': 1, 'unit_price': '1.00'})
        assert_raises_value(settle, None)
        assert_raises_value(settle, ['not a mapping'])
        assert_raises_value(settle, (('quantity', 1),))

    def test_no_mutation(self):
        items = [{'quantity': 2, 'unit_price': '3.5'}]
        before = copy.deepcopy(items)
        out = settle(items, tax_percent='5', discount='1')
        self.assertEqual(items, before)
        self.assertEqual(items[0], before[0])

    def test_extra_keys_ignored(self):
        out = settle([{'quantity': 1, 'unit_price': '5.00', 'sku': 'x'}])
        self.assertEqual(out['line_totals'], ['5.00'])

    def test_tuple_items(self):
        out = settle(({'quantity': 1, 'unit_price': '5.00'},))
        self.assertEqual(out['total'], '5.25')


class TestOutputShape(unittest.TestCase):

    def test_exact_keys(self):
        out = settle([{'quantity': 1, 'unit_price': '10.00'}], tax_percent='10', discount='1')
        self.assertEqual(
            sorted(out),
            ['discount', 'line_totals', 'subtotal', 'tax', 'total'],
        )

    def test_all_monetary_strings(self):
        out = settle([{'quantity': 1, 'unit_price': '10.005'}], tax_percent='10', discount='0')
        values = [out['line_totals'][0], out['subtotal'], out['discount'], out['tax'], out['total']]
        for value in values:
            self.assertIsInstance(value, str)
            self.assertRegex(value, r'^-?\d+\.\d{2}$')
        self.assertEqual(out['line_totals'], ['10.01'])
        self.assertEqual(out['subtotal'], '10.01')
        self.assertEqual(out['discount'], '0.00')
        self.assertEqual(out['tax'], '1.00')
        self.assertEqual(out['total'], '11.01')

    def test_empty_items(self):
        out = settle([], tax_percent='19', discount='0')
        self.assertEqual(out, {
            'line_totals': [],
            'subtotal': '0.00',
            'discount': '0.00',
            'tax': '0.00',
            'total': '0.00',
        })

    def test_negative_zero_avoided(self):
        out = settle([{'quantity': 3, 'unit_price': '-0.00'}], tax_percent='0', discount='0')
        self.assertEqual(out['line_totals'], ['0.00'])
        self.assertEqual(out['total'], '0.00')


class TestDefaults(unittest.TestCase):

    def test_default_arguments(self):
        out = settle([{'quantity': 1, 'unit_price': '100.00'}])
        self.assertEqual(out, {
            'line_totals': ['100.00'],
            'subtotal': '100.00',
            'discount': '0.00',
            'tax': '5.00',
            'total': '105.00',
        })

    def test_keyword_signature(self):
        out = settle([{'quantity': 1, 'unit_price': '100.00'}], tax_percent='5.5', discount='10')
        self.assertEqual(out['tax'], '4.95')
        self.assertEqual(out['total'], '94.95')


if __name__ == '__main__':
    unittest.main(verbosity=2)
