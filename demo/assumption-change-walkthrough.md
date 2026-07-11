# Assumption Change Walkthrough

Company: Example Components Inc. (EXCO)
Scenario: Base reinvestment case
Changed assumption: `fcf_margin_pct` 14.0 -> 16.0

## Movement

- Weighted fair value per share: 37.38 -> 40.02 (+2.64)
- Weighted margin of safety: -11.0% -> -4.7% (+6.3 pts)
- Label: moderate negative gap -> near modeled value

## Steps

- Start with the checked local fixture.
- Change fcf_margin_pct for the selected scenario only.
- Rebuild the deterministic packet with the same model.
- Compare weighted fair value, margin label, and margin-of-safety movement.
- Record the result as research review evidence, not as an action recommendation.

## Boundaries

- Research-only output.
- No live data.
- No broker connections.
- No orders.
- No predictions.
- No buy/sell/hold advice.
