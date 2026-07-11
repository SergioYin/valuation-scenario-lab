# Valuation Scenario Lab v1.2.0 Promotion Deck

Format: static JSON, Markdown, and no-JavaScript HTML

## 1. Problem

Public valuation demos often mix assumptions, narrative, and execution context.

- Readers need static artifacts they can inspect without accounts, feeds, or scripts.
- Reviewers need boundaries and evidence in the same release tree.

Artifacts:
- `README.md`
- `docs/release-checks.md`

## 2. User

Research-oriented investors, analysts, and agent builders evaluating local assumptions.

- The user starts with fictional JSON fixtures.
- The user reviews deterministic Markdown, JSON, HTML, and SVG outputs.

Artifacts:
- `examples/company.json`
- `examples/software-compounder.json`

## 3. Workflow

One command builds the public demo tree and release receipts.

- python -m venv .venv
- . .venv/bin/activate
- pip install -e .
- valuation-scenario-lab demo
- valuation-scenario-lab selfcheck --root .

Artifacts:
- `demo/sample-workflow.html`
- `demo/readme-snippet.html`

## 4. Evidence

The bundled demo for Example Components Inc. (EXCO) produces a fair value snapshot and reviewer scorecard.

- Weighted fair value per share: USD 37.38.
- Reviewer score: 100/100 (strong).
- Fixture doctor, reproducibility audit, manifest, and public bundle are checked locally.

Artifacts:
- `demo/valuation-packet.html`
- `demo/reviewer-scorecard.html`
- `demo/reproducibility-audit.html`
- `release/public-bundle.html`

## 5. Limitations

The project intentionally stops at static research artifacts.

- No live data.
- No broker connections.
- No buy/sell/hold advice.

Artifacts:
- `README.md`
- `skills/agent/valuation-scenario-lab/SKILL.md`

## 6. Repeatability

The release is validated by deterministic commands and checked-in artifacts.

- python -m pytest -q
- valuation-scenario-lab selfcheck --root .
- valuation-scenario-lab validate-release --root . --format markdown

Artifacts:
- `tests/test_cli.py`
- `demo/reproducibility-audit.html`
- `release/release-manifest.json`

## Boundaries

- No live data.
- No broker connections.
- No buy/sell/hold advice.
