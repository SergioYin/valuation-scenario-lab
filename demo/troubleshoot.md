# Troubleshooting Guide

Status: ready
Release validation: pass

## missing-demo-artifact

A demo file is missing after checkout or regeneration.

Run the full deterministic demo and then quickstart validation.

Commands:

- `valuation-scenario-lab demo --root .`
- `valuation-scenario-lab quickstart-check --root . --output demo`

Artifacts:

- `demo/quickstart-check.json`
- `demo/reproducibility-audit.json`

## fixture-doctor-fails

Fixture schema, weights, numeric fields, or source freshness need review.

Run fixture diagnostics and inspect issue paths before rebuilding packets.

Commands:

- `valuation-scenario-lab fixture-doctor --fixtures examples --policy examples/review-policy.json --format markdown`

Artifacts:

- `examples/company.json`
- `examples/review-policy.json`
- `demo/fixture-doctor.md`

## release-validation-fails

Release validation reports missing files, private terms, metadata issues, or boundary gaps.

Generate release receipts, refresh manifests, and rerun validation.

Commands:

- `valuation-scenario-lab install-smoke-receipt --root . --output release`
- `valuation-scenario-lab export-bundle --root . --output release`
- `valuation-scenario-lab release-manifest --root . --output release`
- `valuation-scenario-lab validate-release --root . --format markdown`

Artifacts:

- `release/install-smoke-receipt.json`
- `release/public-bundle.json`
- `release/release-manifest.json`

## schema-mismatch

A generated JSON artifact carries an unexpected schema version.

Regenerate demo and release artifacts with the current package version.

Commands:

- `valuation-scenario-lab demo --root .`
- `valuation-scenario-lab reproducibility-audit --root . --output demo`

Artifacts:

- `demo/reproducibility-audit.json`
- `src/valuation_scenario_lab/release.py`

## scorecard-below-90

Reviewer scorecard is below the strong threshold.

Open each failed criterion and regenerate the command named in its artifacts list.

Commands:

- `valuation-scenario-lab reviewer-scorecard --root . --output demo`
- `valuation-scenario-lab troubleshoot --root . --output demo`

Artifacts:

- `demo/reviewer-scorecard.json`
- `demo/troubleshoot.md`

## empty-directory-wheel-smoke

A wheel-installed user runs commands outside the repository.

Use selfcheck, which falls back to packaged data roots, or pass an explicit unpacked root.

Commands:

- `valuation-scenario-lab selfcheck`
- `valuation-scenario-lab selfcheck --root <repo-or-share-root>`

Artifacts:

- `pyproject.toml`
- `release/install-smoke-receipt.md`

## finance-boundary-concern

A reviewer is concerned the output could be read as advice or live-data backed.

Inspect safety text and regenerate public artifacts that carry the boundaries.

Commands:

- `valuation-scenario-lab reproducibility-audit --root . --output demo`
- `valuation-scenario-lab validate-release --root . --format markdown`

Artifacts:

- `README.md`
- `demo/reproducibility-audit.html`
- `skills/agent/valuation-scenario-lab/SKILL.md`

## Boundaries

- No live data.
- No broker connections.
- No buy/sell/hold advice.
