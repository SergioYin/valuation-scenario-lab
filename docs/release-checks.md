# Release Checks

Run:

```bash
python -m pytest -q
python -m valuation_scenario_lab.cli selfcheck --root .
python -m valuation_scenario_lab.cli quickstart-check --root . --output demo
python -m valuation_scenario_lab.cli visual-receipt --root . --output demo
python -m valuation_scenario_lab.cli showcase-dashboard --root . --output demo
python -m valuation_scenario_lab.cli thesis-brief --root . --output demo
python -m valuation_scenario_lab.cli scenario-library --fixtures examples --output demo
python -m valuation_scenario_lab.cli sample-workflow --root . --output demo
python -m valuation_scenario_lab.cli install-smoke-receipt --root . --output release
python -m valuation_scenario_lab.cli data-dictionary --root . --output release
python -m valuation_scenario_lab.cli operator-handoff --root . --output release
python -m valuation_scenario_lab.cli release-manifest --root . --output release
python -m valuation_scenario_lab.cli export-bundle --root . --output release
python -m valuation_scenario_lab.cli reproducibility-audit --root . --output demo
python -m valuation_scenario_lab.cli new-fixture-template --output demo/onboarding-template
python -m valuation_scenario_lab.cli casebook --root . --output demo
python -m valuation_scenario_lab.cli reviewer-scorecard --root . --output demo
python -m valuation_scenario_lab.cli troubleshoot --root . --output demo
python -m valuation_scenario_lab.cli readme-snippet --root . --output demo
python -m valuation_scenario_lab.cli release-deck --root . --output demo
python -m valuation_scenario_lab.cli fixture-linter-report --root . --output demo
python -m valuation_scenario_lab.cli artifact-catalog --root . --output demo
python -m valuation_scenario_lab.cli data-dictionary --root . --output release
python -m valuation_scenario_lab.cli operator-handoff --root . --output release
python -m valuation_scenario_lab.cli release-manifest --root . --output release
python -m valuation_scenario_lab.cli reproducibility-audit --root . --output demo
python -m valuation_scenario_lab.cli fixture-doctor --fixtures examples --policy examples/review-policy.json --format markdown --output demo
python -m valuation_scenario_lab.cli assumption-change-walkthrough --fixtures examples --output demo
python -m valuation_scenario_lab.cli demo-gallery --fixtures examples --output demo
python -m valuation_scenario_lab.cli decision-journal --packet demo/valuation-packet.json --ledger demo/review-ledger.json --output demo
python -m valuation_scenario_lab.cli public-readiness-landing --root . --output demo
python -m build
valuation-scenario-lab validate-release --format markdown
valuation-scenario-lab maturity-report --format markdown
```

Required demo release artifacts include packet JSON/Markdown/HTML, history comparison JSON/Markdown, review ledger JSON/Markdown, sensitivity matrix JSON/Markdown, assumption-change walkthrough JSON/Markdown/HTML, multi-company demo gallery JSON/Markdown/HTML, decision journal JSON/Markdown, fixture doctor JSON/Markdown, quickstart check JSON/Markdown, visual receipt JSON/Markdown/HTML, showcase dashboard JSON/SVG/Markdown/HTML, thesis brief JSON/Markdown/HTML, scenario library JSON/Markdown/HTML, reproducibility audit JSON/Markdown/HTML, sample workflow JSON/Markdown/HTML, casebook JSON/Markdown/HTML, reviewer scorecard JSON/Markdown/HTML, troubleshooting guide JSON/Markdown/HTML, README snippet JSON/Markdown/HTML, release deck JSON/Markdown/HTML, artifact catalog JSON/Markdown/HTML, fixture linter report JSON/Markdown/HTML, onboarding template README/company/review-policy/prior-packet files, and public readiness landing JSON/Markdown/HTML.

Required release stability artifacts include release manifest JSON/Markdown, install smoke receipt JSON/Markdown/HTML, data dictionary JSON/Markdown/HTML, operator handoff JSON/Markdown/HTML, and public bundle manifest JSON/Markdown/HTML.

The release checks verify required files, demo artifacts, schema versions, hash manifest coverage, bundle coverage, documented install smoke commands, data dictionary coverage, operator handoff placeholders, fixture schema, scenario weights, numeric fields, source staleness warnings, artifact reuse grouping, SHA-256 catalog coverage, public hygiene, safety boundary text, zero dependency package metadata, installed data-file coverage, and absence of workflow automation in this repository.
