# Operator Handoff

Release version: 1.4.0
Validation status: pass

## Repository URL Placeholders

- `repository`: `REPO_URL_PLACEHOLDER`
- `release`: `RELEASE_URL_PLACEHOLDER`
- `wheel`: `WHEEL_URL_PLACEHOLDER`
- `source_archive`: `SOURCE_ARCHIVE_URL_PLACEHOLDER`

## Latest Commands

- `valuation-scenario-lab demo --root .`
- `valuation-scenario-lab data-dictionary --root . --output release`
- `valuation-scenario-lab operator-handoff --root . --output release`
- `valuation-scenario-lab install-smoke-receipt --root . --output release`
- `valuation-scenario-lab export-bundle --root . --output release`
- `valuation-scenario-lab release-manifest --root . --output release`
- `valuation-scenario-lab validate-release --root . --format markdown`

## Release Assets

|

P
a
t
h

|

E
x
i
s
t
s

|

P
a
c
k
a
g
e
d

|

S
H
A
-
2
5
6

|
|

-
-
-

|

-
-
-

|

-
-
-

|

-
-
-

|
| `release/install-smoke-receipt.json` | True | True | `f0f59ce7910e3338bb0fa3febd7aa36ba84b107207f3758233ceb6057859734d` |
| `release/install-smoke-receipt.md` | True | True | `e564926f3fe4e43ba335bc5f0b2deed7a54b6a6237d5382b0234584c963abd6e` |
| `release/install-smoke-receipt.html` | True | True | `615cfc04d8f6669286717c2f1f4d159cea9245886a25364e7796318ead5420fe` |
| `release/operator-handoff.json` | True | True | `a1355020b73198e8ad4c2a32d9217071ee4176cd79d0fd95b1e298d891748355` |
| `release/operator-handoff.md` | True | True | `17f7188093f80a0da9119855a7adbb329b7cc212b9885e28912639dd016b6440` |
| `release/operator-handoff.html` | True | True | `a7cfeac09b3448c554a0d2381c87142e25a9f94206bf20bb1d983d7299d81858` |
| `release/data-dictionary.json` | True | True | `cce338a6dd34b62d565172d42bcb44285c5bd6dd2e276f3260615cc5f07a8c87` |
| `release/data-dictionary.md` | True | True | `d9729bd213a697fbe811894d928b18d345463d7c9b440967205eb7a6de504a5e` |
| `release/data-dictionary.html` | True | True | `b2e9a59b3b03caac9cd76576f08851caf170aa4547ec6ea00017fb8e25189d05` |
| `release/public-bundle.json` | True | True | `08f210ed36a543f657c241d26e77107c63dc80ba4c02ff5e4738b831902dac59` |
| `release/public-bundle.md` | True | True | `7d089542c32f94a9e93f44c3f0e19b05fa8e0af73b65fa4cc130fabd4212e857` |
| `release/public-bundle.html` | True | True | `c38c98bd3c8778b98eda095dc57ba35a9a7c4ee2a2393351fd2f479d8eab054c` |
| `release/release-manifest.json` | True | True | `7aaf4d2916f347f8e8a9be8e5de0f963605be72da266c44b66b2071fec6f9cd2` |
| `release/release-manifest.md` | True | True | `457f4b5cc46c22bdd87e032443050f8972c57ef29ef901e16959463ff8fcf8fb` |

## Validation Results

- schema_version: valuation-scenario-lab.release-validation.v0.8
- status: pass
- finding_count: 0
- error_count: 0
- warning_count: 0

## Known Boundaries

- Research-only output.
- Static local fictional fixtures.
- No live data.
- No broker connections.
- No orders.
- No predictions.
- No buy/sell/hold advice.
- No network access is required by package commands.

## Boundaries

- No live data.
- No broker connections.
- No buy/sell/hold advice.
