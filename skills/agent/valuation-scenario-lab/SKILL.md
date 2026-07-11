# valuation-scenario-lab Agent Protocol

Use this skill when a user asks an agent to generate or review an offline valuation scenario packet from local assumptions.

## Rules

- Treat all outputs as research-only artifacts.
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
11. Summarize generated files, assumptions changed, and research boundaries.

## Public Output Standard

Public summaries should mention that the packet is deterministic, local, broker-free, and research-only. They should not include private paths, private collaboration tools, credentials, tokens, or non-public account details.

Public demo trees should include `public-readiness-landing`, `assumption-change-walkthrough`, `multi-company-demo-gallery`, `decision-journal`, `quickstart-check`, and `visual-receipt` artifacts alongside the valuation packet, history comparison, review ledger, and sensitivity matrix.
