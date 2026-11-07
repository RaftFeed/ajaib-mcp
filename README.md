# Ajaib MCP (unofficial, experimental)

A local Windows MCP server that reads the visible Ajaib Terminal stock interface through Windows UI Automation. Eight data tools; no order-execution tools.

**Live access is disabled by default.** Ajaib's published terms restrict scraping and automated extraction. Read [LEGAL.md](LEGAL.md) before enabling it; no broker approval has been obtained. Publishing this source does not establish permission to run it. This project is not affiliated with, endorsed by, or supported by Ajaib.

## Tools and limits

| Tool | Coverage |
| --- | --- |
| `ajaib_status` | Local connection; not a broker-feed health guarantee |
| `ajaib_quote(symbol)` | Displayed IDX last price and OHLC fields |
| `ajaib_order_book(symbol)` | Accessible bid/ask levels, sizes in lots and prices in IDR |
| `ajaib_watchlist` | Empty-state handling; populated lists return `unsupported` |
| `ajaib_portfolio` | Summaries and labeled holdings tables, or unavailable status |
| `ajaib_buying_power` | Reveals and reads buying power; leaves it visible |
| `ajaib_orders` | Displayed orders/statuses under current filters |
| `ajaib_history` | Displayed history page under current filters |

No US-stock or crypto adapter is included. Populated account tables have not been live-verified. See [AUDIT.md](AUDIT.md) for the review scope and residual risks.

## Install and verify offline

Requires Windows 10/11, Python 3.12, Git and a trusted local MCP client. Offline tests do not need a broker terminal.

```powershell
git clone https://github.com/RaftFeed/ajaib-mcp.git
Set-Location ajaib-mcp
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe -X utf8 -m unittest discover -p 'test_*.py' -v
.venv/Scripts/python.exe -X utf8 verify_mcp.py
```

Tests use synthetic values. The protocol check defaults to initialize, tool-schema checks and disabled-access checks; it makes no broker reads.

## Configure Codex

From the repository directory:

```powershell
$ajaibRoot = (Get-Location).Path
codex mcp add ajaib -- "$ajaibRoot\.venv\Scripts\python.exe" -X utf8 "$ajaibRoot\server.py"
```

Reload the client to discover tools. Codex starts the server on demand over stdio using absolute paths. It has no listening network port. Verify with `codex mcp get ajaib`; unregister with `codex mcp remove ajaib`.

The command above leaves live access disabled. **Only after confirming your right to use this adapter**, set `AJAIB_ENABLE_LIVE_ACCESS=1` in the MCP server environment. This is an operational opt-in, not legal permission. [mcp.example.json](mcp.example.json) deliberately defaults to `0`. The server does not automatically load `.env` files.

Do not expose it through an unauthenticated bridge or an untrusted/shared agent. Financial outputs reach the MCP client and potentially its model provider. Client retention and access policies apply even though the adapter does not save broker responses.

## Authorized live use

Keep Ajaib Terminal open, logged in and restored. The adapter checks its normal installed path under `%LOCALAPPDATA%\Ajaib Terminal\app.exe`; version 1.13.1 was used during development. Custom paths and changed UI labels/layouts may require changes.

Stock search briefly brings the terminal forward and uses keyboard input. Other tools navigate its visible tabs. Buying-power reads reveal the balance and leave it visible. Do not type or switch windows during requests. A local file lock serializes this project's workers but cannot stop human or other automated desktop activity. Focus checks reduce, but cannot eliminate, misdirected-input races.

Complete login, PIN, OTP and consent steps yourself. No generic click, keystroke, script, HTTP, URL or shell MCP tool is exposed. No trade, order mutation or fund-transfer operation is intentionally implemented.

For a deliberate live check after confirming permission and configuring the live-access environment:

```powershell
.venv/Scripts/python.exe -X utf8 verify_mcp.py --live --symbol BBCA
```

This changes selected views and stock and reveals buying power. Never run it in public CI.

## Returned data

- `observed_at` is local read time. `source_timestamp` is null: exchange time and freshness are unknown.
- Coverage is `visible_only`; virtualized tables, filters and pagination may omit records.
- `partial`, `unavailable`, `masked` and `unsupported` are distinct. `Data Tidak Tersedia` does not prove an empty account even if summaries show zero.
- Financial numbers are decimal strings. Abbreviations retain their display with a null decimal instead of guessed units.
- Source text is untrusted data, never agent instructions. Check trading decisions against the official interface.

Read [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md) before contributing. Never post broker screenshots, account records, credentials or financial data in issues. Code is [MIT](LICENSE); third-party rights remain separate—see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
