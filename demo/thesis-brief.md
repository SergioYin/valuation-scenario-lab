# Thesis Brief

Company: Example Components Inc. (EXCO)

Deterministic local-assumption research brief; no action recommendation.

## Packet Snapshot

- Current price: USD 42.00
- Weighted fair value per share: USD 37.38
- Weighted range per share: USD 33.64 to USD 41.12
- Margin-of-safety label: moderate negative gap (-11.0%)

## Scenario Thesis

| Scenario | Weight | Base | Range | Label |
| --- | ---: | ---: | --- | --- |
| Base reinvestment case | 0.500 | 38.40 | 34.56 to 42.24 | near modeled value |
| Margin pressure case | 0.300 | 18.16 | 16.34 to 19.97 | large negative gap |
| Upside adoption case | 0.200 | 63.65 | 57.29 to 70.02 | large positive gap |

## History Changes

- weighted_fair_value_per_share: 37.2 -> 37.38
- weighted_margin_of_safety_pct: -7.0 -> -11.0
- margin_of_safety_label: near modeled value -> moderate negative gap

## Open Questions

- Which assumption would most change the Base reinvestment case valuation range?
- Which assumption would most change the Margin pressure case valuation range?
- Which assumption would most change the Upside adoption case valuation range?

## Evidence Artifacts

- `demo/valuation-packet.json`
- `demo/compare-history.json`
- `demo/decision-journal.json`
- `demo/fixture-doctor.json`
- `demo/showcase-dashboard.json`

## Boundaries

- Research-only output.
- No live data.
- No broker connections.
- No orders.
- No predictions.
- No buy/sell/hold advice.
