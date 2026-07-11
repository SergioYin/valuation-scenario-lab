# Release Notes

## v0.6.0

Showcase dashboard release.

This release adds `showcase-dashboard`, a zero-runtime-dependency command that writes deterministic JSON, SVG, Markdown, and static no-JavaScript HTML from the current demo packet, multi-company gallery, fixture doctor report, and sensitivity matrix. The SVG is shareable as a standalone public visual while keeping the same local-fixture research boundaries as the rest of the project.

`demo`, `quickstart-check`, `selfcheck`, release validation, package data, README CTAs, release docs, and tests now include the showcase dashboard artifacts. Runtime dependencies remain zero.

Boundaries: no live data, no broker connections, no orders, no predictions, and no buy/sell/hold advice.

## v0.5.0

Fixture depth and release validation hardening release.

This release adds `fixture-doctor`, a zero-runtime-dependency command that reports fixture schema, scenario weight, numeric-field, and source staleness issues in JSON or Markdown. `selfcheck`, `quickstart-check`, `validate-release`, generated demos, package data, and release docs now include the doctor output.

The test suite now includes golden snapshots for key deterministic demo outputs and malformed fixture coverage for both fixture diagnostics and packet build failure paths. Runtime dependencies remain zero.

Boundaries: no live data, no broker connections, no orders, no predictions, and no buy/sell/hold advice.

## v0.4.0

Promotion hardening release for public demos.

This release adds a second neutral bundled fixture, `examples/software-compounder.json`, plus deterministic `assumption-change-walkthrough` and `demo-gallery` commands. The new commands write JSON, Markdown, and static HTML artifacts so reviewers can inspect how one changed local assumption moves the model and compare multiple fictional demo companies without live data.

Release validation, package data, README examples, docs, tests, and release manifest coverage require the v0.4 artifacts. Runtime dependencies remain zero.

Boundaries: no live data, no broker connections, no orders, no predictions, and no buy/sell/hold advice.

## v0.3.0

`valuation-scenario-lab` is a zero-runtime-dependency Python CLI for turning local valuation assumptions into Markdown, JSON, and static no-JavaScript HTML research packets.

This release includes `selfcheck --root` support, installed fixture fallback for wheel users, deterministic `quickstart-check` receipts, deterministic `visual-receipt` JSON, Markdown, and HTML artifacts, a `decision-journal` command for review records, and a static `public-readiness-landing` command for first-screen public release checks.

Boundaries: no live data, no broker connections, no orders, no predictions, and no buy/sell/hold advice.
