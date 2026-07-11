# Data Dictionary

Release version: 1.4.0

## Scope

- company fixtures
- valuation packets
- review ledgers
- decision journals
- reviewer scorecards
- artifact catalogs
- fixture linter reports
- release receipts

## Company Fixture

Artifacts: `examples/company.json`, `examples/software-compounder.json`, `demo/onboarding-template/company.json`

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `company` | string | True | Fictional company display name. |
| `ticker` | string | False | Fictional ticker or local identifier. |
| `currency` | string | False | Currency label used for generated packet display. |
| `template_note` | string | False | Onboarding note for scaffold fixtures. |
| `current_price` | number | True | Static local reference price used only for deterministic gap math. |
| `shares_outstanding_m` | number | True | Static share count in millions. |
| `net_cash_m` | number | True | Static net cash balance in millions. |
| `source_freshness` | array<object> | False | Fixture-level source freshness entries with name and age_days. |
| `scenarios` | array<object> | True | Weighted local scenario assumptions; weights must sum to 1.0. |
| `scenarios[].name` | string | True | Scenario label. |
| `scenarios[].weight` | number | True | Scenario probability weight. |
| `scenarios[].starting_revenue_m` | number | True | Starting revenue in millions. |
| `scenarios[].revenue_growth_pct` | number | True | Five-year annual revenue growth percentage. |
| `scenarios[].fcf_margin_pct` | number | True | Free-cash-flow margin percentage. |
| `scenarios[].discount_rate_pct` | number | True | Discount rate percentage. |
| `scenarios[].terminal_growth_pct` | number | True | Terminal growth percentage. |
| `scenarios[].terminal_multiple` | number | True | Terminal multiple cross-check. |
| `scenarios[].catalysts` | array<string> | False | Local catalyst notes. |
| `scenarios[].risks` | array<string> | False | Local risk notes. |
| `scenarios[].source_freshness` | array<object> | False | Scenario-level source freshness entries. |

## Valuation Packet

Artifacts: `demo/valuation-packet.json`, `examples/prior-packet.json`

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `schema_version` | string | True | Packet schema identifier. |
| `generated_on` | string | True | Static generation marker. |
| `company` | string | True | Company display name. |
| `ticker` | string | True | Ticker or local identifier. |
| `currency` | string | True | Currency label. |
| `current_price` | number | True | Rounded static reference price. |
| `weighted_fair_value_per_share` | number | True | Scenario-weighted modeled fair value per share. |
| `weighted_range_per_share` | array<number> | True | Scenario-weighted low and high range. |
| `weighted_margin_of_safety_pct` | number | True | Modeled percentage gap versus current_price. |
| `margin_of_safety_label` | string | True | Neutral label for modeled value gap. |
| `valuation_ranges` | array<object> | True | Per-scenario low/base/high outputs. |
| `valuation_ranges[].scenario` | string | True | Scenario name. |
| `valuation_ranges[].weight` | number | True | Scenario weight. |
| `valuation_ranges[].low` | number | True | Low value per share. |
| `valuation_ranges[].base` | number | True | Blended base value per share. |
| `valuation_ranges[].high` | number | True | High value per share. |
| `valuation_ranges[].margin_of_safety_pct` | number | True | Scenario value gap percentage. |
| `valuation_ranges[].margin_label` | string | True | Scenario neutral gap label. |
| `valuation_ranges[].score` | number | True | Internal deterministic review score. |
| `catalysts` | array<string> | True | Sorted catalyst notes from scenarios. |
| `risks` | array<string> | True | Sorted risk notes from scenarios. |
| `source_freshness` | array<object> | True | Fixture source freshness entries. |
| `review_prompts` | array<string> | True | Neutral review prompts. |
| `boundaries` | array<string> | True | Finance safety boundaries. |

## Review And Scorecard Outputs

Artifacts: `demo/review-ledger.json`, `demo/decision-journal.json`, `demo/reviewer-scorecard.json`

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `entries` | array<object> | False | Review ledger rows. |
| `entries[].scenario` | string | False | Scenario under review. |
| `entries[].priority` | string | False | Review priority bucket. |
| `entries[].margin_label` | string | False | Neutral gap label. |
| `entries[].review_question` | string | False | Question for local review. |
| `entries[].owner` | string | False | Local owner placeholder. |
| `entries[].evidence` | array<string> | False | Evidence artifact paths. |
| `journal_entries` | array<object> | False | Decision journal rows. |
| `summary_decision` | string | False | No-action research logging summary. |
| `open_questions` | array<string> | False | Open review questions. |
| `status` | string | False | Scorecard status. |
| `score` | number | False | Awarded score. |
| `max_score` | number | False | Maximum score. |
| `rubric` | string | False | Scorecard rubric description. |
| `lenses` | array<object> | False | Product, engineering, cold-user, and risk score lenses. |
| `lenses[].criteria` | array<object> | False | Criteria with max points, awarded points, status, and artifacts. |

## Catalog And Linter Outputs

Artifacts: `demo/artifact-catalog.json`, `demo/fixture-linter-report.json`

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `artifact_count` | number | False | Catalog artifact count. |
| `package_data_count` | number | False | Number of artifacts included as package data. |
| `required_release_file_count` | number | False | Count of required release files present in catalog. |
| `groups` | array<object> | False | Catalog groups by audience and reuse purpose. |
| `groups[].audience` | string | True | Target reviewer audience. |
| `groups[].purposes` | array<object> | True | Reuse-purpose buckets. |
| `groups[].purposes[].artifacts` | array<object> | True | Artifact rows with path, category, format, hash, size, flags, and usage note. |
| `fixture_source` | string | False | Fixture directory label. |
| `fixture_count` | number | False | Number of fixture files inspected. |
| `issue_count` | number | False | Total fixture diagnostic count. |
| `severity_counts` | object | False | Counts by error, warning, and info. |
| `diagnostics` | array<object> | False | Fixture doctor issues with remediation commands. |
| `release_checks` | object | False | Release context for the linter report. |
| `safety_summary` | object | False | Safety-boundary coverage summary. |

## Release Receipts

Artifacts: `release/install-smoke-receipt.json`, `release/public-bundle.json`, `release/release-manifest.json`, `release/operator-handoff.json`, `release/data-dictionary.json`

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `network_policy` | string | False | Offline install-smoke policy text. |
| `install_commands` | array<object> | False | Documented local install commands and expected output. |
| `entry_point_smoke_commands` | array<object> | False | Documented CLI smoke commands and expected output. |
| `expected_files` | array<object> | False | Expected release file existence checks. |
| `files` | array<object> | False | Manifest or bundle file rows with path, hash, bytes, category, package-data flag, and usage note. |
| `self_outputs` | array<object> | False | Outputs excluded from self hash indexing. |
| `repo_url_placeholders` | object | False | Repository, release, wheel, and source archive URL placeholders. |
| `latest_commands` | array<string> | False | Final local handoff command list. |
| `release_assets` | array<object> | False | Final release asset rows. |
| `validation_results` | object | False | Release validation status and finding counts. |
| `known_boundaries` | array<string> | False | Operational boundaries for handoff. |
| `sections` | array<object> | False | Data dictionary schema sections. |
| `format_notes` | array<string> | False | Data dictionary format notes. |

## Format Notes

- Fields are deterministic JSON keys emitted or consumed by the offline CLI.
- Numeric valuation fields are rounded in generated artifacts for stable review.
- All paths are repository-relative unless explicitly marked as placeholders.

## Boundaries

- No live data.
- No broker connections.
- No buy/sell/hold advice.
