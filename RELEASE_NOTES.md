# Release Notes

## v0.4.0

Promotion hardening release for public demos.

This release adds a second neutral bundled fixture, `examples/software-compounder.json`, plus deterministic `assumption-change-walkthrough` and `demo-gallery` commands. The new commands write JSON, Markdown, and static HTML artifacts so reviewers can inspect how one changed local assumption moves the model and compare multiple fictional demo companies without live data.

Release validation, package data, README examples, docs, tests, and release manifest coverage now require the new v0.4 artifacts. Runtime dependencies remain zero.

Boundaries: no live data, no broker connections, no orders, no predictions, and no buy/sell/hold advice.

## v0.3.0

`valuation-scenario-lab` is a zero-runtime-dependency Python CLI for turning local valuation assumptions into Markdown, JSON, and static no-JavaScript HTML research packets.

This release includes `selfcheck --root` support, installed fixture fallback for wheel users, deterministic `quickstart-check` receipts, deterministic `visual-receipt` JSON, Markdown, and HTML artifacts, a `decision-journal` command for review records, and a static `public-readiness-landing` command for first-screen public release checks.

Boundaries: no live data, no broker connections, no orders, no predictions, and no buy/sell/hold advice.
