# valuation-scenario-lab

Build deterministic, broker-free valuation scenario packets from local assumptions.

Target user: research-oriented individual investors, analysts, and agent builders who want auditable Markdown, JSON, and no-JavaScript HTML artifacts before any live data or execution system is involved.

## Quickstart

First actions:

- Run the complete deterministic demo: `valuation-scenario-lab demo`
- Share the static visual dashboard: `demo/showcase-dashboard.svg` or `demo/showcase-dashboard.html`
- Open the first public artifact: `demo/public-readiness-landing.html`
- Validate release readiness: `valuation-scenario-lab validate-release --format markdown`
- Review boundaries before reuse: no live data, no broker connections, no buy/sell/hold advice.

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
valuation-scenario-lab demo
valuation-scenario-lab selfcheck --root .
valuation-scenario-lab quickstart-check --root . --output demo
valuation-scenario-lab visual-receipt --root . --output demo
valuation-scenario-lab showcase-dashboard --root . --output demo
valuation-scenario-lab thesis-brief --root . --output demo
valuation-scenario-lab scenario-library --fixtures examples --output demo
valuation-scenario-lab sample-workflow --root . --output demo
valuation-scenario-lab reproducibility-audit --root . --output demo
valuation-scenario-lab new-fixture-template --output demo/onboarding-template
valuation-scenario-lab casebook --root . --output demo
valuation-scenario-lab fixture-doctor --fixtures examples --policy examples/review-policy.json --format markdown --output demo
valuation-scenario-lab assumption-change-walkthrough --fixtures examples --output demo
valuation-scenario-lab demo-gallery --fixtures examples --output demo
valuation-scenario-lab decision-journal --packet demo/valuation-packet.json --ledger demo/review-ledger.json --output demo
valuation-scenario-lab public-readiness-landing --root . --output demo
valuation-scenario-lab build-packet --fixtures examples --output demo
valuation-scenario-lab compare-history --current demo/valuation-packet.json --prior examples/prior-packet.json --output demo
valuation-scenario-lab review-ledger --packet demo/valuation-packet.json --policy examples/review-policy.json --output demo
valuation-scenario-lab sensitivity-matrix --fixtures examples --output demo
valuation-scenario-lab validate-release --format markdown
valuation-scenario-lab maturity-report --format markdown
valuation-scenario-lab release-manifest --output release
```

Example output:

```text
Weighted fair value per share: USD 37.38
Weighted range per share: USD 33.64 to USD 41.12
Margin-of-safety label: moderate negative gap (-11.0%)
```

Open `demo/showcase-dashboard.svg`, `demo/showcase-dashboard.html`, `demo/thesis-brief.html`, `demo/scenario-library.html`, `demo/casebook.html`, `demo/sample-workflow.html`, `demo/reproducibility-audit.html`, `demo/public-readiness-landing.html`, `demo/valuation-packet.md`, `demo/valuation-packet.json`, or `demo/valuation-packet.html` to inspect the checked-in packet. The demo also includes `compare-history`, `review-ledger`, `sensitivity-matrix`, `assumption-change-walkthrough`, `multi-company-demo-gallery`, `decision-journal`, `fixture-doctor`, `quickstart-check`, `visual-receipt`, and `onboarding-template` artifacts.

Wheel-installed users can run `valuation-scenario-lab selfcheck` from an empty current directory. The command falls back to the packaged fixtures installed under `share/valuation-scenario-lab`. Use `--root <repo-or-share-root>` to point selfcheck at a specific unpacked release tree.

## Boundaries

- No live data.
- No broker connections.
- No orders.
- No predictions.
- No buy/sell/hold advice.
- Research-only output from explicit local assumptions.

This package does not fetch market prices, connect to accounts, place orders, rank securities, or tell a user what to buy, sell, or hold.

## Commands

- `build-packet`: read `company.json` and write deterministic packet Markdown, JSON, and static HTML.
- `compare-history`: compare a current packet with a prior packet fixture.
- `review-ledger`: create scenario-level review prompts and priority buckets.
- `sensitivity-matrix`: vary discount-rate and FCF-margin inputs around the first scenario.
- `assumption-change-walkthrough`: show how a single changed local assumption moves the deterministic packet.
- `demo-gallery`: build a neutral multi-company gallery from bundled company fixtures.
- `decision-journal`: log scenario review decisions, evidence, and open questions without trade recommendations.
- `public-readiness-landing`: write a static public landing artifact with first actions, demo outputs, readiness checks, and boundaries.
- `fixture-doctor`: report fixture schema, scenario weight, numeric-field, and source staleness issues as JSON or Markdown.
- `selfcheck`: regenerate artifacts in a temporary directory and run release hygiene checks; accepts `--root`.
- `quickstart-check`: regenerate demo files and write deterministic quickstart JSON and Markdown receipts.
- `visual-receipt`: write deterministic JSON, Markdown, and static HTML receipts for a demo packet.
- `showcase-dashboard`: write deterministic JSON, SVG, Markdown, and static HTML dashboard artifacts from the demo packet, gallery, fixture doctor, and sensitivity matrix.
- `thesis-brief`: compose deterministic JSON, Markdown, and static HTML analyst brief artifacts from packet, compare-history, decision-journal, fixture-doctor, and showcase-dashboard inputs.
- `scenario-library`: export reusable scenario assumption cards from bundled company fixtures as JSON, Markdown, and static HTML.
- `sample-workflow`: write a deterministic analyst workflow receipt linking primary commands to their JSON, Markdown, HTML, SVG, and release artifacts.
- `reproducibility-audit`: write deterministic JSON, Markdown, and static HTML audit receipts for artifact presence, schema versions, hash manifest coverage, zero dependency metadata, and safety boundaries.
- `new-fixture-template`: write a fictional documented company fixture, review policy, and prior packet template into an onboarding output directory.
- `casebook`: write public JSON, Markdown, and static HTML walkthroughs tying the packet, scenario library, thesis brief, workflow receipt, and reproducibility audit together for a new reader.
- `validate-release`: verify required public files, generated demos, safety strings, and private-reference hygiene.
- `maturity-report`: score release readiness from validation findings.
- `release-manifest`: emit file hashes for public release review.

## Fixture Shape

`examples/company.json` and `examples/software-compounder.json` contain neutral fictional company metadata, current reference price, share count, net cash, source freshness entries, and weighted valuation scenarios. Each scenario includes revenue, revenue growth, FCF margin, discount rate, terminal growth, terminal multiple, catalysts, risks, and source freshness.

All inputs are static JSON. Keep fixtures generic and local. Do not include account identifiers, client records, broker exports, API keys, or private notes.

Run `valuation-scenario-lab fixture-doctor --fixtures examples --policy examples/review-policy.json --format markdown` before publishing fixture changes. Schema, weight, and numeric issues fail validation; staleness issues are warnings unless they also break fixture shape.

## Development

```bash
pip install -e .
python -m pytest -q
python -m valuation_scenario_lab.cli selfcheck
```

The package has zero runtime dependencies and uses only the Python standard library.
