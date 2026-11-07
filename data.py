"""Pure parsing; financial decimals are strings, never binary floats."""
from datetime import datetime
from decimal import Decimal, InvalidOperation
import re


def symbol(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Z][A-Z0-9]{0,11}', value):
        raise ValueError('Use an uppercase IDX symbol, e.g. BBCA (maximum 12 characters).')
    return value


def number(display):
    if not isinstance(display, str) or len(display) > 128:
        return None
    text = display.strip().replace('−', '-')
    if text.startswith('Rp'):
        text = text[2:].strip()
    if text.endswith('%'):
        text = text[:-1].strip()
    if not re.fullmatch(r'[+-]?(?:\d{1,3}(?:\.\d{3})+|\d+)(?:,\d+)?', text):
        return None
    try:
        return str(Decimal(text.replace('.', '').replace(',', '.')))
    except InvalidOperation:
        return None


def result(status, data=None, warnings=None):
    return dict(source='Ajaib Terminal / Windows UI Automation',
                observed_at=datetime.now().astimezone().isoformat(),
                source_timestamp=None, status=status, coverage='visible_only',
                warnings=['Exchange timestamp and quote freshness are not established.'] + (warnings or []),
                data=data)


def field(value):
    return {'display': value, 'decimal': number(value)}


def buying_power(tokens):
    if 'Buying Power' not in tokens:
        return None
    for text in tokens[tokens.index('Buying Power') + 1:]:
        if text in ('Deposit', 'Trade', 'Est. Total Aset', 'Return (P&L)'):
            break
        if text.startswith('Rp') and number(text) is not None:
            return field(text)
    return None


def quote(tokens, ticker):
    # The symbol button precedes company, leverage badge, price and change.
    start = tokens.index(ticker)
    end = tokens.index('Chart', start)
    header = tokens[start + 1:end]
    numeric = [x for x in header if number(x) is not None]
    if not numeric:
        raise ValueError('Stock detail price is unavailable.')
    values = {'symbol': ticker, 'currency': 'IDR', 'last_price': field(numeric[0]),
              'header_display': header}
    for name in ('Open', 'High', 'Low', 'Prev', 'ARA', 'ARB', 'Lot', 'Val', 'Avg'):
        if name in tokens:
            i = tokens.index(name)
            if i + 1 < len(tokens):
                values[name.lower()] = field(tokens[i + 1])
    return values


def order_book(tokens, ticker):
    bid = tokens.index('BID')
    ask = tokens.index('ASK', bid)
    end = tokens.index('Total', ask)
    left, right = tokens[bid + 1:ask], tokens[ask + 1:end]
    # Ask header follows the ASK label; bid header precedes BID.
    if right[:2] != ['LOT', 'FREQ']:
        raise ValueError('Unknown order-book header layout.')
    right = right[2:]
    if len(left) % 3 or len(right) % 3 or not left or not right:
        raise ValueError('Incomplete order-book rows; retry after loading.')
    def rows(values, side):
        parsed = []
        for i in range(0, len(values), 3):
            triple = values[i:i+3]
            freq, lots, price = triple if side == 'bid' else triple[::-1]
            if any(number(x) is None for x in triple):
                raise ValueError('Unrecognized order-book value.')
            parsed.append(dict(price=field(price), lots=field(lots), frequency=field(freq)))
        return parsed
    return dict(symbol=ticker, currency='IDR', size_unit='lot',
                bids=rows(left, 'bid'), asks=rows(right, 'ask'))
