import unittest
from data import buying_power, number, order_book, quote, result, symbol


class DataTests(unittest.TestCase):
    def test_localized_decimal_and_masked_values(self):
        for original, expected in [('Rp1.234,50', '1234.50'), ('-0,09%', '-0.09'), ('1.250', '1250'), ('0', '0'), ('******', None), ('-', None), ('9.87B', None), ('Rp1Rp2', None), ('1%2', None), ('1' * 129, None)]:
            self.assertEqual(number(original), expected)

    def test_symbol_boundary(self):
        for invalid in ['bbca', 'BBCA{ENTER}', 'BBCA;exit', '', 'A' * 13, 'B B']:
            with self.assertRaises(ValueError):
                symbol(invalid)
        self.assertEqual(symbol('BBCA'), 'BBCA')

    def test_order_book_sides_and_units(self):
        parsed = order_book(['BID', '2', '30', '1.000', 'ASK', 'LOT', 'FREQ', '1.010', '40', '3', 'Total'], 'DEMO')
        self.assertEqual(parsed['bids'][0]['price']['decimal'], '1000')
        self.assertEqual(parsed['asks'][0]['lots']['decimal'], '40')
        self.assertEqual(parsed['asks'][0]['frequency']['decimal'], '3')
        self.assertEqual(parsed['size_unit'], 'lot')
        with self.assertRaises(ValueError):
            order_book(['BID', '24', '700', 'ASK', 'LOT', 'FREQ', 'Total'], 'BBCA')

    def test_quote_ignores_leverage_and_preserves_display(self):
        parsed = quote(['DEMO', 'Synthetic company', '10x', '1.250', '0', '(', '0', '%)', 'Chart', 'Open', '1.200'], 'DEMO')
        self.assertEqual(parsed['last_price']['decimal'], '1250')
        self.assertEqual(parsed['open']['decimal'], '1200')

    def test_unavailable_is_not_empty_account(self):
        parsed = result('unavailable')
        self.assertIsNone(parsed['data'])
        self.assertIsNone(parsed['source_timestamp'])
        self.assertIn('observed_at', parsed)

    def test_buying_power_cannot_be_confused_with_total_assets(self):
        self.assertIsNone(buying_power(['Buying Power', 'Deposit', 'Trade', 'Est. Total Aset', 'Rp123']))
        self.assertIsNone(buying_power(['Buying Power', '******', 'Deposit']))
        self.assertEqual(buying_power(['Buying Power', 'Hide buying power', 'Rp1.234,50', 'Deposit'])['decimal'], '1234.50')


if __name__ == '__main__':
    unittest.main()
