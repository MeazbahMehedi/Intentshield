# IntentShield branding update — 25 October 2026

- Renamed the project, root folder, Python package/imports, UI labels, translations, GitHub workflow title and exported scan filenames.
- Replaced the brand mark with a protected-conversation SVG logo and added the matching favicon and README logo.
- Updated the full README with technologies, architecture, workflow and migration guidance.
- Preserved rules, all dataset JSON and historical evaluation JSON byte for byte; retained existing page layout, styles, configuration variables and model integration behavior.
- Preserved existing database and browser preference compatibility. A fresh installation uses `intentshield.sqlite3`; an existing `promptguard.sqlite3` is opened in place when the new filename is absent.
- Verified 98 tests, both bundled browser checks, and matching default-policy analysis for all 1,637 dataset cases, excluding source fingerprints and latency.

# GitHub Developers update — 25 October 2026

- Fixed the Developers page accounts to MeazbahMehedi and ItsMONIKAAKTER in server source.
- Added public GitHub profile names, avatars, bios, metadata, counts and links.
- Added paginated public repository listings for both accounts, with search, developer filter and sorting.
- Added background synchronization, a 15-minute cache, five-minute error retry, stale-data fallback and explicit empty/unavailable/partial states.
- Removed editable profile placeholders; no website account-editing controls or GitHub write endpoint exists.
- Verified 98 automated tests, the existing core browser flows, and developer-page desktop/mobile fixture checks. Live public profile/repository synchronization succeeded for both accounts; avatars use a safe initials fallback when image loading is unavailable.

# Upgrade notes — 24 October 2026

- Replaced cookie-only history with scoped SQLite scan/evaluation/policy/audit persistence.
- Added a layered engine with independent injection, safety, sensitive-data and source results.
- Added bounded decoding and variant provenance, with redacted matched evidence.
- Added optional development-trained lexical ML and rules/hybrid/ML evaluation modes.
- Added an editable enforcement policy and privacy/retention controls.
- Added Evaluation Lab, Untrusted Sources, Security Gateway, Audit Trail, scan detail and Developers pages.
- Added dataset leakage audit, overlap filtering, grouped metrics and versioned experiment comparisons/exports.
- Added a dry-run gateway and optional Ollama adapter with input/source/output inspection and explicit tool permissions.
- Added optional hashed accounts, roles, service token, CSRF, size limits, quotas and browser security headers.
- Removed inactive top-level duplicate UI/routes and unused milestone placeholders.
- Rewrote README, API/security/architecture/requirements documentation and evaluation snapshots.
- Verified with 90 automated tests and desktop/mobile browser flows; real Ollama HTTP behavior is mocked in automated verification.
