# Fixture Linter Report

Status: pass
Fixture source: `examples`
Fixture count: 2
Issues: 0 (errors 0, warnings 0, info 0)

## Files

- `examples/company.json`: pass
- `examples/software-compounder.json`: pass

## Diagnostics

- none

## Remediation Commands

- `valuation-scenario-lab fixture-doctor --fixtures examples --format markdown`
- `valuation-scenario-lab build-packet --fixtures examples --output demo`
- `valuation-scenario-lab quickstart-check --root . --output demo`
- `valuation-scenario-lab validate-release --root . --format markdown`

## Release Checks

- Required files: pass
- Schema versions: pass
- Release validation: fail

## Safety Summary

- Status: pass
- Files checked: 35
- Files missing boundaries: 0

## Boundaries

- No live data.
- No broker connections.
- No buy/sell/hold advice.
