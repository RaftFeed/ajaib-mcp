"""Ajaib-only UI adapter. No order operations and no generic action endpoint."""
import os
from pathlib import Path
import time
import psutil
from pywinauto import Desktop
from data import buying_power, field, order_book, quote, result, symbol

EXPECTED = Path(os.environ['LOCALAPPDATA']) / 'Ajaib Terminal' / 'app.exe'
SAFE = {('Hyperlink', 'Stocks'), ('Hyperlink', 'Portfolio'),
        ('TabItem', 'Aset'), ('TabItem', 'Order'), ('TabItem', 'Riwayat'),
        ('Button', 'Show buying power')}


def validate_snapshot(nodes):
    for node in nodes:
        name = node['name'].casefold()
        if node.get('password') or any(word in name for word in (
                'masukkan pin', 'enter pin', 'kode otp', 'verification code',
                'masuk ke akun', 'sign in', 'konfirmasi order')):
            raise RuntimeError('Authentication or confirmation view detected; handle it manually.')
        if node['role'] == 'Window' or node.get('modal') or node.get('aria_role') in ('dialog', 'alertdialog'):
            raise RuntimeError('Unexpected dialog detected; handle it manually.')


class Terminal:
    def __init__(self):
        self.window = Desktop(backend='uia').window(title='Ajaib Terminal').wrapper_object()
        actual = Path(psutil.Process(self.window.process_id()).exe())
        if actual.resolve() != EXPECTED.resolve():
            raise RuntimeError('Terminal executable identity mismatch.')

    def guard(self):
        if Path(psutil.Process(self.window.process_id()).exe()).resolve() != EXPECTED.resolve():
            raise RuntimeError('Terminal executable identity mismatch.')
        if not self.window.is_visible() or self.window.is_minimized():
            raise RuntimeError('Restore the Ajaib Terminal window before reading data.')
        docs = self.window.descendants(control_type='Document')
        if not docs or docs[0].element_info.name != 'Ajaib Trade':
            raise RuntimeError('Unexpected terminal document; no navigation performed.')
        if self.window.descendants(control_type='Window'):
            raise RuntimeError('A terminal dialog is open; handle it manually first.')
        nodes = self.nodes()
        validate_snapshot(nodes)

    def nodes(self):
        root = self.window.descendants(control_type='Document')[0]
        output = []
        characters = 0
        def visit(control, depth=0):
            nonlocal characters
            if depth > 40 or len(output) >= 5000:
                raise RuntimeError('Terminal accessibility tree exceeds safety bounds.')
            info = control.element_info
            if info.control_type == 'Document':
                return  # Embedded chart has a different numeric locale.
            name = info.name or ''
            characters += len(name)
            if len(name) > 4096 or characters > 1_000_000:
                raise RuntimeError('Terminal text exceeds safety bounds.')
            output.append({'role': info.control_type, 'name': name,
                           'password': bool(info.element.CurrentIsPassword),
                           'aria_role': info.element.CurrentAriaRole,
                           'modal': 'modal=true' in info.element.CurrentAriaProperties})
            for child in control.children():
                visit(child, depth + 1)
        for child in root.children():
            visit(child)
        return output

    def tokens(self):
        return [n['name'].strip() for n in self.nodes()
                if n['role'] in ('Text', 'Button', 'HeaderItem', 'DataItem')
                and n['name'].strip() and '\ufffc' not in n['name']]

    def search_focused(self, combo):
        import win32gui
        from pywinauto.uia_defines import IUIA
        focused = IUIA().iuia.GetFocusedElement()
        if win32gui.GetForegroundWindow() != self.window.handle:
            return False
        if focused.CurrentProcessId != combo.element_info.process_id:
            return False
        if focused.CurrentName == 'Cari saham | Ctrl+K':
            return True
        # ARIA activedescendant reports the suggestion as focused while the
        # keyboard still belongs to the combobox. Require its actual UIA role,
        # expanded popup, same process, and no exposed background navigation.
        return ((focused.CurrentAriaRole == 'option'
                 or (focused.CurrentControlType == 50033 and focused.CurrentName == 'Ajaib Trade'))
                and 'expanded=true' in combo.element_info.element.CurrentAriaProperties
                and not self.window.descendants(control_type='Hyperlink'))

    def activate(self, role, name):
        if (role, name) not in SAFE:
            raise ValueError('Operation is outside the read-only navigation allowlist.')
        self.guard()
        if not self.window.descendants(control_type='Hyperlink'):
            self.window.set_focus()
            combos = self.window.descendants(control_type='ComboBox')
            if len(combos) == 1 and self.search_focused(combos[0]):
                self.window.type_keys('{ESC}', set_foreground=False)
                time.sleep(.2)
                self.guard()
        found = [c for c in self.window.descendants(control_type=role)
                 if c.element_info.name == name and c.is_enabled() and c.is_visible()]
        if len(found) != 1:
            raise RuntimeError('Expected one safe navigation control; terminal layout changed.')
        if role == 'TabItem':
            found[0].select()
        else:
            found[0].invoke()
        time.sleep(.35)
        self.guard()

    def portfolio_view(self, tab):
        self.activate('Hyperlink', 'Portfolio')
        deadline = time.monotonic() + 5
        while not self.window.descendants(control_type='TabItem'):
            if time.monotonic() > deadline:
                raise RuntimeError('Portfolio navigation timed out.')
            time.sleep(.2)
        self.activate('TabItem', tab)
        selected = [c.element_info.name for c in self.window.descendants(control_type='TabItem') if c.is_selected()]
        if selected != [tab]:
            raise RuntimeError('Portfolio tab selection was not confirmed.')
        # The data view may have asynchronous loading after the tab selection.
        time.sleep(.6)
        self.guard()

    def select_stock(self, ticker):
        ticker = symbol(ticker)
        self.guard()
        combos = [c for c in self.window.descendants(control_type='ComboBox')
                  if c.element_info.name == 'Cari saham | Ctrl+K']
        if len(combos) != 1:
            raise RuntimeError('Verified stock search field is unavailable.')
        # React search requires keyboard input, not UIA SetValue. Only validated
        # alphanumerics enter this exact search field; no arbitrary keystroke tool.
        combo = combos[0]
        self.window.set_focus()
        if not self.search_focused(combo):
            # WebView ignores UIA SetFocus. Resolve this one named control's
            # current clickable point; never use saved coordinates.
            import win32gui
            point = combo.rectangle().mid_point()
            owner = win32gui.GetAncestor(win32gui.WindowFromPoint((point.x, point.y)), 2)
            if owner != self.window.handle:
                raise RuntimeError('Stock search is covered by another window; no input performed.')
            combo.click_input()
            time.sleep(.5)
        if not self.search_focused(combo):
            raise RuntimeError('Stock search focus could not be verified. Bring Ajaib Terminal to the foreground.')
        combo.type_keys('^a' + ticker, set_foreground=False, pause=.04)
        deadline = time.monotonic() + 6
        while time.monotonic() < deadline:
            self.guard()
            found = [c for c in self.window.descendants(control_type='ListItem')
                     if c.element_info.name.startswith(ticker + ' ' + ticker + ' ')]
            if len(found) == 1:
                found[0].invoke()
                break
            time.sleep(.25)
        else:
            raise RuntimeError('Exact stock search result not found; no symbol selected.')
        deadline = time.monotonic() + 6
        while time.monotonic() < deadline:
            self.guard()
            if any(c.element_info.name == ticker for c in self.window.descendants(control_type='Button')):
                time.sleep(.7)
                return ticker
            time.sleep(.25)
        raise RuntimeError('Selected stock symbol was not confirmed.')

    def table_data(self):
        tables = []
        characters = 0
        row_count = 0
        for table in self.window.descendants(control_type='Table'):
            rows = []
            for row in table.children():
                cells = [c.element_info.name for c in row.children()]
                row_count += 1
                characters += sum(len(cell) for cell in cells)
                if (row_count > 5000 or len(cells) > 64 or
                        any(len(cell) > 4096 for cell in cells) or characters > 1_000_000):
                    raise RuntimeError('Terminal table exceeds safety bounds.')
                if cells:
                    rows.append(cells)
            tables.append(rows)
        return tables

    def run(self, action, ticker=None):
        self.guard()
        if action == 'status':
            return result('ok', {'connected': True, 'terminal_version_tested': '1.13.1',
                          'capabilities': ['watchlist', 'quote', 'order_book', 'portfolio', 'buying_power', 'orders', 'history'],
                          'read_only': True, 'navigation_changes_visible_view': True})
        if action in ('quote', 'order_book'):
            ticker = self.select_stock(ticker)
            tokens = self.tokens()
            try:
                data = quote(tokens, ticker) if action == 'quote' else order_book(tokens, ticker)
            except ValueError:
                return result('unavailable', warnings=['Required stock-detail fields are absent or layout changed.'])
            return result('partial', data, ['Visible terminal fields only; historical close and live price are not distinguished.'])
        if action == 'watchlist':
            self.activate('Hyperlink', 'Stocks')
            tokens = self.tokens()
            if 'Watchlist masih kosong' in tokens:
                return result('ok', {'entries': [], 'display': 'Watchlist masih kosong'},
                              ['Only the currently selected watchlist is covered.'])
            return result('unsupported', warnings=['A populated watchlist was detected, but its row layout has not been verified. No unrelated portfolio or trade tables are substituted.'])
        if action in ('portfolio', 'orders', 'history'):
            self.portfolio_view({'portfolio': 'Aset', 'orders': 'Order', 'history': 'Riwayat'}[action])
            tokens = self.tokens()
            if 'Data Tidak Tersedia' in tokens:
                return result('unavailable', warnings=['Ajaib displays Data Tidak Tersedia. Do not interpret zero summaries as an empty account.'])
            summary = {}
            for label in ('Est. Total Aset', 'Return (P&L)', 'Diinvestasikan'):
                if label in tokens and tokens.index(label) + 1 < len(tokens):
                    summary[label] = field(tokens[tokens.index(label) + 1])
            return result('partial', {'summary': summary, 'tables': self.table_data()},
                          ['Displayed rows only; current filters and pagination apply. Order statuses are preserved without assuming all orders are open.'])
        if action == 'buying_power':
            self.portfolio_view('Aset')
            tokens = self.tokens()
            if any(c.element_info.name == 'Show buying power' for c in self.window.descendants(control_type='Button')):
                self.activate('Button', 'Show buying power')
                tokens = self.tokens()
            value = buying_power(tokens)
            if value is not None:
                return result('partial', {'buying_power': value, 'currency': 'IDR'}, ['Account feed validity must be confirmed separately.'])
            return result('masked' if '******' in tokens else 'unavailable', warnings=['Buying power was not exposed as an unambiguous currency value.'])
        raise ValueError('Unknown read-only data operation.')
