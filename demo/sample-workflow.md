# Sample Analyst Workflow Receipt

Status: pass

## Steps

### 1. Generate the full demo tree

Command: `valuation-scenario-lab demo --root .`

- `demo/valuation-packet.json`: ok
- `demo/valuation-packet.md`: ok
- `demo/valuation-packet.html`: ok

### 2. Compare against prior assumptions

Command: `valuation-scenario-lab compare-history --current demo/valuation-packet.json --prior examples/prior-packet.json --output demo`

- `demo/compare-history.json`: ok
- `demo/compare-history.md`: ok

### 3. Create review evidence

Command: `valuation-scenario-lab review-ledger --packet demo/valuation-packet.json --policy examples/review-policy.json --output demo`

- `demo/review-ledger.json`: ok
- `demo/review-ledger.md`: ok

### 4. Stress local assumptions

Command: `valuation-scenario-lab sensitivity-matrix --fixtures examples --output demo`

- `demo/sensitivity-matrix.json`: ok
- `demo/sensitivity-matrix.md`: ok

### 5. Explain one assumption change

Command: `valuation-scenario-lab assumption-change-walkthrough --fixtures examples --output demo`

- `demo/assumption-change-walkthrough.json`: ok
- `demo/assumption-change-walkthrough.md`: ok
- `demo/assumption-change-walkthrough.html`: ok

### 6. Review fixture quality

Command: `valuation-scenario-lab fixture-doctor --fixtures examples --policy examples/review-policy.json --format markdown --output demo`

- `demo/fixture-doctor.json`: ok
- `demo/fixture-doctor.md`: ok

### 7. Summarize analyst outputs

Command: `valuation-scenario-lab thesis-brief --root . --output demo`

- `demo/thesis-brief.json`: ok
- `demo/thesis-brief.md`: ok
- `demo/thesis-brief.html`: ok

### 8. Publish static demo views

Command: `valuation-scenario-lab public-readiness-landing --root . --output demo`

- `demo/public-readiness-landing.json`: ok
- `demo/public-readiness-landing.md`: ok
- `demo/public-readiness-landing.html`: ok
- `demo/showcase-dashboard.svg`: ok
- `demo/showcase-dashboard.html`: ok
- `demo/scenario-library.html`: ok

### 9. Record release reproducibility

Command: `valuation-scenario-lab reproducibility-audit --root . --output demo`

- `demo/reproducibility-audit.json`: ok
- `demo/reproducibility-audit.md`: ok
- `demo/reproducibility-audit.html`: ok
- `release/release-manifest.json`: ok
- `release/release-manifest.md`: ok

## Boundaries

- No live data.
- No broker connections.
- No buy/sell/hold advice.
