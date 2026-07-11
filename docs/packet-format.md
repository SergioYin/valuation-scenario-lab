# Packet Format

The packet combines company assumptions, weighted scenarios, DCF-style free-cash-flow estimates, terminal-value cross-checks, valuation ranges, margin-of-safety labels, catalysts, risks, source freshness notes, review prompts, and explicit research boundaries.

The model is intentionally simple and deterministic. It is a reproducible research artifact, not a prediction engine or recommendation system.

Related deterministic artifacts:

- `decision-journal` records scenario review decisions, evidence files, and open questions while preserving the no-advice boundary.
- `assumption-change-walkthrough` changes one local scenario assumption and records before/after movement without making a recommendation.
- `demo-gallery` summarizes multiple neutral bundled fixtures for public demos without live data.
- `fixture-doctor` validates fixture shape, scenario weights, numeric fields, and source staleness without fetching live data.
- `public-readiness-landing` summarizes first actions, demo outputs, release checks, and public boundaries in JSON, Markdown, and static HTML.
- `data-dictionary` documents company fixture, packet, scorecard, catalog, linter, and release receipt schema fields.
- `operator-handoff` summarizes final release commands, release assets, validation results, URL placeholders, and known boundaries.
