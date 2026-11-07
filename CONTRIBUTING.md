# Contributing

Use Windows and Python 3.12. Install `requirements.txt`, run `python -m unittest discover -p 'test_*.py' -v`, then `python verify_mcp.py` with the virtual environment. Defaults must remain offline. Never run live broker checks in CI.

Include synthetic regression tests for parser, validation, privacy and navigation-boundary changes. Preserve decimal strings and unavailable/masked/unsupported states. Do not add trade execution, generic UI controls, credential extraction, unrestricted scripts or network listeners under the read-only contract.

Never commit `.venv`, private paths, account data, market dumps, credentials, browser traces or screenshots. Review the staged diff and tracked file list before pushing. Public reports should use synthetic inputs, expected output, platform versions and the affected module.

Update documentation and audit findings when behavior or assumptions change. Dependency updates must pass unit tests and vulnerability scans. Contributions use MIT; contribute only material you can license.
