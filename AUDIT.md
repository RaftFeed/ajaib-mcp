# Security and publication audit

Date: 2026-11-07 (Asia/Jakarta). Scope: all project Python modules/tests, dependency pins, MCP configuration, public documentation and CI. Method: manual code/data-flow review, offline regression/protocol checks, Bandit, detect-secrets, pip-audit and a review of official published legal sources. This is not an independent penetration test, formal legal opinion or guarantee of safety.

## Findings

| ID | Severity | Finding | Disposition |
| --- | --- | --- | --- |
| LEGAL-01 | High contractual risk | Published broker terms restrict automated extraction; no permission has been obtained | Unresolved; live access defaults off. See [LEGAL.md](LEGAL.md). Source publication is not clearance to operate |
| SEC-01 | Medium privacy risk | The original server allowed account reads immediately after registration | Fixed with explicit environment opt-in in [server.py](server.py#L41) and [worker.py](worker.py#L10); offline tests verify denial before launching/attaching the adapter |
| SEC-02 | Low data-integrity risk | Replacing currency/percent markers anywhere could turn malformed `Rp1Rp2` or `1%2` into a different number | Fixed in [data.py](data.py#L13): markers only at boundaries, bounded input, malformed formats rejected; regression tests added |
| SEC-03 | Low availability risk | Per-node text and generic table responses lacked text/row/cell bounds | Fixed with bounded text and tables in [terminal.py](terminal.py#L46) and [table_data](terminal.py#L175). A blocked UIA call still relies on the worker timeout |
| RES-01 | Medium desktop-interaction risk | Focus/overlay can change after checks and before physical keyboard input | Not eliminated. [select_stock](terminal.py#L131) checks identity/focus/covering windows. Explicit opt-in and exclusive desktop use reduce exposure; they do not make this race impossible |
| RES-02 | Medium privacy risk | Tool outputs may be retained by an MCP client or forwarded to a model provider | User/client trust boundary documented in [SECURITY.md](SECURITY.md); not solved by avoiding local logs |
| RES-03 | Low supply-chain risk | Exact package pins are not wheel-hash verification; same-user code/executable replacement is outside the trust boundary | Documented. CI actions are commit-pinned; no dependencies or broker binaries are vendored |

No additional high/critical exploitable code issue was identified in this scoped review. That statement does not resolve the high contractual risk or certify the code.

## Checks performed

- **11 offline unit tests passed**: localized decimals, malformed markers and oversized values, input allowlist, bid/ask mapping and units, quote parsing, unavailable versus empty, buying-power boundaries, rejection of trading controls, authentication/modal guards, server/direct-worker opt-in enforcement, and worker error-output handling.
- **MCP protocol passed**: initialize, eight read-only tool definitions, and live-access denial by default. No broker terminal was read during the publication audit.
- **Dependency audit**: pip-audit found no known vulnerabilities in the 34 pinned runtime distributions. This is a point-in-time database result, not proof of absence.
- **Static analysis**: Bandit reported two low-severity advisories, B404 and B603, in [server.py](server.py#L6) and its subprocess call. Manual review accepted them: executable/script are locally fixed, shell execution is not enabled, tool input is JSON on stdin, and no user-controlled command is executed. Findings were not hidden through scanner suppression.
- **Secret/publication review**: detect-secrets 1.5.0 reported no candidate secrets in the public source candidate set. A separate scan checked for private Windows user paths, development workspace identifiers and known private identity text. The staged manifest was reviewed before commit; local environments/provenance files are excluded.
- Dependency metadata/license inventory is recorded in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). This is metadata review, not exhaustive legal analysis of every upstream file.

## Historical live verification, not repeated here

Before this audit, development checks exercised the eight tools through stdio against Terminal 1.13.1. Quote/order-book reads and buying-power display worked; the selected watchlist was empty, and portfolio/orders/history displayed unavailable data. No actual account data or captured market dataset is included in this release.

The release adds access gating and output/parser safeguards. These changes have offline regression coverage; they have not been revalidated with new live broker reads. Populated account-table extraction, every possible layout/dialog, signed-executable identity, all focus races, and legal permission remain unverified. Generic account tables may omit virtualized or paginated rows. Populated watchlist parsing is unsupported.

## Publication boundary

The public source contains synthetic numeric fixtures and no account identifiers, credentials, screenshots, browser traces, holdings, balances, broker binaries, model transcripts or virtual environment. No GitHub Actions job uses a live broker or account secret. CI is configured for offline Windows tests and dependency auditing; remote run results must be checked separately rather than inferred from this file.
