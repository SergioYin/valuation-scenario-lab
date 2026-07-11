# Release Checks

Run:

```bash
python -m pytest -q
python -m valuation_scenario_lab.cli selfcheck --root .
python -m valuation_scenario_lab.cli quickstart-check --root . --output demo
python -m valuation_scenario_lab.cli visual-receipt --root . --output demo
python -m valuation_scenario_lab.cli decision-journal --packet demo/valuation-packet.json --ledger demo/review-ledger.json --output demo
python -m valuation_scenario_lab.cli public-readiness-landing --root . --output demo
python -m build
valuation-scenario-lab validate-release --format markdown
valuation-scenario-lab maturity-report --format markdown
```

Required demo release artifacts include packet JSON/Markdown/HTML, history comparison JSON/Markdown, review ledger JSON/Markdown, sensitivity matrix JSON/Markdown, decision journal JSON/Markdown, quickstart check JSON/Markdown, visual receipt JSON/Markdown/HTML, and public readiness landing JSON/Markdown/HTML.

The release checks verify required files, demo artifacts, public hygiene, safety boundary text, package metadata, installed data-file coverage, and absence of workflow automation in this repository.
