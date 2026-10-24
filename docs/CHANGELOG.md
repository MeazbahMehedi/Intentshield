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
