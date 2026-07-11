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

### 10. Score reviewer operability

Command: `valuation-scenario-lab reviewer-scorecard --root . --output demo`

- `demo/reviewer-scorecard.json`: ok
- `demo/reviewer-scorecard.md`: ok
- `demo/reviewer-scorecard.html`: ok

### 11. Map common diagnostics

Command: `valuation-scenario-lab troubleshoot --root . --output demo`

- `demo/troubleshoot.json`: ok
- `demo/troubleshoot.md`: ok
- `demo/troubleshoot.html`: ok

### 12. Prepare public promotion snippets

Command: `valuation-scenario-lab readme-snippet --root . --output demo && valuation-scenario-lab release-deck --root . --output demo`

- `demo/readme-snippet.json`: ok
- `demo/readme-snippet.md`: ok
- `demo/readme-snippet.html`: ok
- `demo/release-deck.json`: ok
- `demo/release-deck.md`: ok
- `demo/release-deck.html`: ok

### 13. Document install and bundle stability

Command: `valuation-scenario-lab install-smoke-receipt --root . --output release && valuation-scenario-lab export-bundle --root . --output release`

- `release/install-smoke-receipt.json`: ok
- `release/install-smoke-receipt.md`: ok
- `release/install-smoke-receipt.html`: ok
- `release/public-bundle.json`: ok
- `release/public-bundle.md`: ok
- `release/public-bundle.html`: ok

## Boundaries

- No live data.
- No broker connections.
- No buy/sell/hold advice.
