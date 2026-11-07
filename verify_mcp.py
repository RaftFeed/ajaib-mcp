"""Run against the live terminal. Prints statuses only; stores no account data."""
import asyncio
import argparse
import json
import os
from pathlib import Path
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main(live=False, ticker='BBCA'):
    if live and os.environ.get('AJAIB_ENABLE_LIVE_ACCESS') != '1':
        raise SystemExit('Live checks require explicit AJAIB_ENABLE_LIVE_ACCESS=1 and broker permission; see LEGAL.md.')
    server = StdioServerParameters(command=sys.executable, args=['-X', 'utf8', str(Path(__file__).with_name('server.py').resolve())])
    async with stdio_client(server) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            assert len(tools) == 8
            assert all(t.annotations.readOnlyHint and not t.annotations.destructiveHint for t in tools)
            print('initialize and tools/list: PASS (8 read-only tools)', flush=True)
            if not live:
                response = await session.call_tool('ajaib_status', {})
                assert response.isError, 'Offline verification requires live access to be disabled.'
                print('default live-access denial: PASS (no broker access)', flush=True)
                return
            for name, arguments in [
                ('ajaib_status', {}), ('ajaib_quote', {'symbol': ticker}),
                ('ajaib_order_book', {'symbol': ticker}), ('ajaib_watchlist', {}),
                ('ajaib_portfolio', {}), ('ajaib_orders', {}),
                ('ajaib_history', {}), ('ajaib_buying_power', {}),
            ]:
                response = await session.call_tool(name, arguments)
                assert not response.isError, (name, 'MCP returned an error')
                value = json.loads(response.content[0].text)
                assert value['observed_at'] and value['source_timestamp'] is None
                assert value['status'] in {'ok', 'partial', 'unavailable', 'masked', 'unsupported'}
                if name == 'ajaib_quote':
                    assert value['data']['symbol'] == ticker and value['data']['last_price']['decimal'] is not None
                if name == 'ajaib_order_book':
                    assert value['data']['symbol'] == ticker and value['data']['bids'] and value['data']['asks']
                print(f'{name}: PASS ({value["status"]})', flush=True)
            for invalid in ({'symbol': 'BBCA{ENTER}'}, {'symbol': 123}, {}):
                response = await session.call_tool('ajaib_quote', invalid)
                assert response.isError
            print('invalid input handling: PASS', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true', help='Opt into reads/navigation and buying-power reveal; broker permission required.')
    parser.add_argument('--symbol', default='BBCA')
    args = parser.parse_args()
    if not args.live:
        os.environ['AJAIB_ENABLE_LIVE_ACCESS'] = '0'
    asyncio.run(main(args.live, args.symbol))
