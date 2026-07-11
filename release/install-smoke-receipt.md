# Install Smoke Receipt

Status: documented

No network commands are run by this receipt; install commands are documented for offline/local wheel validation.

## Install Commands

- local wheel: `python -m pip install --no-index --find-links dist valuation_scenario_lab-1.4.0-py3-none-any.whl`
  Expected: `Successfully installed valuation-scenario-lab-1.4.0`
- editable local checkout: `python -m pip install -e .`
  Expected: `Successfully installed valuation-scenario-lab-1.4.0`

## Entry Point Smoke Commands

- `valuation-scenario-lab --version`
  Expected: `1.4.0`
- `valuation-scenario-lab selfcheck`
  Expected: `selfcheck passed`
- `valuation-scenario-lab install-smoke-receipt --root . --output release`
  Expected: `wrote release/install-smoke-receipt.json`
- `valuation-scenario-lab export-bundle --root . --output release`
  Expected: `wrote release/public-bundle.json`
- `valuation-scenario-lab operator-handoff --root . --output release`
  Expected: `wrote release/operator-handoff.json`
- `valuation-scenario-lab data-dictionary --root . --output release`
  Expected: `wrote release/data-dictionary.json`
- `valuation-scenario-lab validate-release --root . --format markdown`
  Expected: `Status: pass`

## Expected Files

- `dist/valuation_scenario_lab-1.4.0-py3-none-any.whl`: ok
- `dist/valuation_scenario_lab-1.4.0.tar.gz`: ok
- `release/public-bundle.json`: ok
- `release/public-bundle.md`: ok
- `release/public-bundle.html`: ok
- `release/operator-handoff.json`: ok
- `release/operator-handoff.md`: ok
- `release/operator-handoff.html`: ok
- `release/data-dictionary.json`: ok
- `release/data-dictionary.md`: ok
- `release/data-dictionary.html`: ok

## Boundaries

- No live data.
- No broker connections.
- No buy/sell/hold advice.
