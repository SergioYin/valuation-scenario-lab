# valuation-scenario-lab Agent Protocol

Use this skill when a user asks an agent to generate or review an offline valuation scenario packet from local assumptions.

## Rules

- Treat all outputs as research-only artifacts.
- No live data.
- No broker connections.
- No buy/sell/hold advice.
- Do not fetch live market data.
- Do not connect to broker, custody, bank, or execution systems.
- Do not place, route, stage, or simulate orders.
- Do not provide buy, sell, or hold advice.
- Keep fixtures free of private account, client, token, and broker-export data.
- Prefer `valuation-scenario-lab selfcheck --root <root>` before sharing generated artifacts.
- Use packaged fixtures only for command health checks; do not present them as live company research.

## Workflow

1. Inspect `examples/company.json` or the user-provided fixture directory.
2. Run `valuation-scenario-lab build-packet --fixtures <fixtures> --output <output>`.
3. If a prior packet exists, run `compare-history`.
4. Run `review-ledger` and `sensitivity-matrix` for review evidence.
5. Run `assumption-change-walkthrough` when explaining how one local assumption changes the packet.
6. Run `demo-gallery` when preparing a neutral multi-company public demo.
7. Run `decision-journal` to log scenario review decisions and open questions without trade recommendations.
8. Run `valuation-scenario-lab public-readiness-landing --root <root> --output <output>` when preparing a public demo tree.
9. Run `valuation-scenario-lab quickstart-check --root <root> --output <output>` when checking public demo files.
10. Run `valuation-scenario-lab visual-receipt --root <root> --output <output>` when a deterministic Markdown/HTML receipt is useful.
11. Run `valuation-scenario-lab thesis-brief --root <root> --output <output>` to compose a deterministic analyst brief from packet, history, journal, doctor, and dashboard artifacts.
12. Run `valuation-scenario-lab scenario-library --fixtures <fixtures> --output <output>` to export reusable assumption cards from bundled fictional fixtures.
13. Run `valuation-scenario-lab sample-workflow --root <root> --output <output>` to record the primary command and artifact chain.
14. Run `valuation-scenario-lab reproducibility-audit --root <root> --output <output>` to record deterministic artifact, schema, hash-manifest, dependency, and safety-boundary checks.
15. Run `valuation-scenario-lab new-fixture-template --output <output>/onboarding-template` when a new user needs a fictional fixture, review policy, and prior packet scaffold.
16. Run `valuation-scenario-lab casebook --root <root> --output <output>` to create a stranger-readable public walkthrough tying packet, scenario library, thesis brief, workflow receipt, and reproducibility audit artifacts together.
17. Run `valuation-scenario-lab reviewer-scorecard --root <root> --output <output>` to score product, engineering, cold-user, and risk operability from local artifacts.
18. Run `valuation-scenario-lab troubleshoot --root <root> --output <output>` to map common failure modes to diagnostic commands and artifacts.
19. Run `valuation-scenario-lab readme-snippet --root <root> --output <output>` to create the shortest public quickstart, boundaries, and artifact map for promotion.
20. Run `valuation-scenario-lab release-deck --root <root> --output <output>` to create static promotion slides for problem, user, workflow, evidence, limitations, and repeatability.
21. Run `valuation-scenario-lab fixture-linter-report --root <root> --output <output>` to create expanded fixture diagnostics with severity counts, paths, remediation commands, release checks, and safety summary.
22. Run `valuation-scenario-lab artifact-catalog --root <root> --output <output>` to create a reuse catalog grouping demo, release, docs, skill, package data, release note, changelog, and test artifacts by audience and reuse purpose with hashes.
23. Run `valuation-scenario-lab install-smoke-receipt --root <root> --output release` to document local wheel install commands, entry point smoke commands, and expected outputs without running network.
24. Run `valuation-scenario-lab export-bundle --root <root> --output release` to create a deterministic public bundle manifest with hashes and usage notes for demo, release, package data, docs, tests, and skill files.
25. Summarize generated files, assumptions changed, and research boundaries.

## Public Output Standard

Public summaries should mention that the packet is deterministic, local, broker-free, and research-only. They should not include private paths, private collaboration tools, credentials, tokens, or non-public account details.

Public demo trees should include `public-readiness-landing`, `assumption-change-walkthrough`, `multi-company-demo-gallery`, `decision-journal`, `quickstart-check`, `visual-receipt`, `thesis-brief`, `scenario-library`, `sample-workflow`, `reproducibility-audit`, `casebook`, `reviewer-scorecard`, `troubleshoot`, `readme-snippet`, `release-deck`, `fixture-linter-report`, `artifact-catalog`, and `onboarding-template` artifacts alongside the valuation packet, history comparison, review ledger, and sensitivity matrix. Release trees should include `release-manifest`, `install-smoke-receipt`, and `public-bundle` artifacts.
