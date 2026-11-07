# Project context

## Purpose and architecture

Unofficial experimental Windows stdio MCP for read-only Ajaib Terminal observations. `server.py` registers eight tools and calls a timed worker. `worker.py` enforces a cross-process lock and imports the UIA adapter only after explicit live-access opt-in. `terminal.py` verifies the installed executable path and implements fixed data-view operations. `data.py` parses displayed financial values without binary floats. No broker credentials, generic UI commands, network listener or trade operations are implemented.

## Constraints and open risks

Live access defaults disabled unless `AJAIB_ENABLE_LIVE_ACCESS=1`; it is not broker permission. See [LEGAL.md](LEGAL.md), [SECURITY.md](SECURITY.md) and [AUDIT.md](AUDIT.md). The official terms raise unresolved automated-extraction restrictions. Do not run further live checks without confirming applicable permission. No live broker reads were made during the publication audit.

Physical stock-search input has a remaining focus race. Account outputs can reach the MCP client/model provider. Populated watchlists are unsupported; populated holdings/order/history extraction is not live-verified. Coverage is visible-only and exchange timestamps are unknown. Do not weaken these limits or label the project legally cleared or production-secure.

## Setup and verification

Windows, Python 3.12; `python -m venv .venv` and `.venv/Scripts/python.exe -m pip install -r requirements.txt`. Run unit tests using `python -m unittest discover -p 'test_*.py' -v`; `python verify_mcp.py` performs offline protocol/access-denial checks. `--live` is deliberate and also requires the environment opt-in. Never run it in CI.

## Latest checkpoint — 2026-11-07, Asia/Jakarta

Public source prepared with MIT license, contributor/security/legal/audit docs, dependency inventory, offline Windows workflow and Dependabot. Eleven offline unit tests and MCP handshake/access-denial checks passed. Dependency audit: no known vulnerabilities. Bandit: two reviewed low subprocess advisories; secret scan: no findings. Historical live verification belongs to the pre-audit prototype and is explicitly distinguished in AUDIT.md. Public source excludes local provenance, environments and all account data. Repository destination: RaftFeed/ajaib-mcp; publication and remote CI are verified operationally after commit rather than claimed by this context file.
