# Public Readiness Landing

Offline valuation scenario lab

Deterministic Markdown, JSON, and static HTML artifacts from local assumptions.

## CTAs

- Run the demo: `valuation-scenario-lab demo` -> `demo/valuation-packet.html`
- Validate release: `valuation-scenario-lab validate-release --format markdown` -> `release/release-manifest.md`
- Read the journal: `valuation-scenario-lab decision-journal --packet demo/valuation-packet.json --ledger demo/review-ledger.json --output demo` -> `demo/decision-journal.md`
- Read the thesis brief: `valuation-scenario-lab thesis-brief --root . --output demo` -> `demo/thesis-brief.md`
- Export scenario cards: `valuation-scenario-lab scenario-library --fixtures examples --output demo` -> `demo/scenario-library.html`
- Doctor fixtures: `valuation-scenario-lab fixture-doctor --fixtures examples --policy examples/review-policy.json --format markdown` -> `demo/fixture-doctor.md`

## Demo Outputs

- `demo/valuation-packet.html`
- `demo/quickstart-check.md`
- `demo/visual-receipt.html`
- `demo/showcase-dashboard.svg`
- `demo/showcase-dashboard.html`
- `demo/thesis-brief.html`
- `demo/scenario-library.html`
- `demo/decision-journal.md`
- `demo/assumption-change-walkthrough.html`
- `demo/multi-company-demo-gallery.html`
- `demo/fixture-doctor.md`
- `demo/public-readiness-landing.html`

## Readiness Checks

- zero runtime dependencies
- static local fixtures
- deterministic demo artifacts
- fixture doctor schema, weight, numeric, and staleness checks
- public-neutral boundary text
- no workflow automation

## Boundaries

- Research-only output.
- No live data.
- No broker connections.
- No orders.
- No predictions.
- No buy/sell/hold advice.
