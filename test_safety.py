import unittest
from terminal import Terminal, validate_snapshot


class SafetyTests(unittest.TestCase):
    def test_trading_controls_are_rejected_before_touching_the_ui(self):
        adapter = Terminal.__new__(Terminal)
        for role, name in [('Button', 'Beli'), ('Button', 'Sell'), ('Button', 'Deposit'),
                           ('Button', 'Trade'), ('Button', 'Cancel'), ('Hyperlink', 'https://example.com')]:
            with self.assertRaises(ValueError):
                adapter.activate(role, name)

    def test_authentication_and_unknown_dialogs_block_navigation(self):
        for node in [dict(role='Edit', name='', password=True),
                     dict(role='Text', name='Masukkan PIN'),
                     dict(role='Group', name='', aria_role='dialog'),
                     dict(role='Group', name='', modal=True)]:
            with self.assertRaises(RuntimeError):
                validate_snapshot([node])
        validate_snapshot([dict(role='Text', name='Buying Power')])


if __name__ == '__main__':
    unittest.main()
