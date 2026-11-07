# Security policy

Experimental software; no production-security certification or support SLA. Report vulnerabilities privately through the repository Security tab → Report a vulnerability. If private reporting is unavailable, request a private contact in an issue without including exploit details or sensitive data.

Never include account identifiers, credentials, OTPs, screenshots, broker responses, balances or holdings in public reports. Use affected code, a synthetic reproduction and impact. Never test someone else's account.

## Trust and data flow

Trusted local MCP client → stdio server → bounded worker subprocess → current user's terminal UI → financial output → MCP client/model provider.

Live access defaults off; it requires `AJAIB_ENABLE_LIVE_ACCESS=1`. No network transport, listening port, authentication bypass or credential reader is implemented. The broker and MCP client/model may themselves use the network. Do not wrap this server in an unauthenticated HTTP bridge.

The current Windows account, local executable, installed dependencies and MCP client are trusted. Same-user attackers who can replace code, the Python environment or broker executable are outside the isolation boundary. Path checks are not code-signature verification or a sandbox. Do not run as administrator.

## Controls and residual risks

- Fixed data/navigation operations and bounded uppercase symbols; no generic UI or shell tool. The subprocess uses an absolute local script and no shell.
- Window/process/focus checks reduce accidental input. Another program or a human can still change focus after a check. Do not share the desktop during reads. Read-only tool schemas cannot make physical input harmless in every race.
- A file lock serializes this project's workers, not other desktop activity. Reads time out after 50 seconds. Partial UI changes may remain after cancellation or timeout.
- Password/authentication fields and unknown modal dialogs stop navigation. Detection is defensive, not proof that every future app version/dialog is recognized.
- Node, row, cell and text bounds limit responses. Unknown numeric formats fail parsing. Broker text remains untrusted even inside JSON.
- The adapter does not deliberately persist or log broker responses. They still reach the MCP client/model and may remain in memory, client histories or OS crash/page files. Buying power becomes visible on screen.
- Dependency scans are point-in-time checks, not proof of safety. Review dependency and license changes.

See [AUDIT.md](AUDIT.md) for findings and [LEGAL.md](LEGAL.md) for unresolved broker terms.
