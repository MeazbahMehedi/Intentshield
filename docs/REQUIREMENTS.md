# Software requirements specification — PromptGuard 3

## 1. Purpose and scope

Provide a local web workspace that detects known AI input threats, explains evidence, applies configurable policies, evaluates labeled test corpora and demonstrates prevention through a controlled language-model gateway. Intended users are students, researchers and local administrators. It is a coursework/research prototype, with optional hosted controls rather than a certified production security product.

## 2. Users and interfaces

Local mode supports a browser session without login. Optional authenticated roles are administrator (can write policy) and analyst (can scan/evaluate). A service token permits only scan, batch, document and gateway operations. The browser provides separate pages for scanning, evidence, analytics, probes, policies, source inspection, experiments, gateway, audits, profiles, integrations and settings.

## 3. Functional requirements and verification

| ID | Requirement | Implemented component / evidence |
|---|---|---|
| FR-01 | Accept non-empty text with explicit size/type validation | Main/advanced routes; input-validation tests |
| FR-02 | Identify known injection, jailbreak, extraction and tool-misuse signals | Existing rules + layered engine; detector regressions |
| FR-03 | Keep harmful-content findings separate from injection score | Safety layer; independent-intent regression |
| FR-04 | Inspect bounded obfuscated/encoded copies, preserving original hash | normalization.py; encoding parameterized tests |
| FR-05 | Identify sensitive-data patterns with redacted evidence | engine.py; raw/encoded secret regressions |
| FR-06 | Treat externally sourced instructions as untrusted data | Source metadata/unmasked source checks; document regression |
| FR-07 | Apply configurable ALLOW/WARN/REVIEW/BLOCK policies | policy.py and editor; validation/threshold tests |
| FR-08 | Optionally train and run a lexical ML baseline on development only | semantic.py; training-metadata test |
| FR-09 | Evaluate labeled corpora and expose metrics/groups/misses | evaluation.py; lab integration tests |
| FR-10 | Audit schema and overlap, exclude candidate leakage in clean runs | Dataset audit; filtered-count test |
| FR-11 | Save versioned experiment metadata and compare compatible runs | Experiment hashes/comparison endpoint tests |
| FR-12 | Export scan/evaluation data and provide printable reports | CSV/JSON endpoints, browser Print/Save PDF |
| FR-13 | Stop input/source REVIEW/BLOCK before backend execution | Gateway; mocked backend non-invocation tests |
| FR-14 | Restrict optional tools to explicitly enabled calculator | Bounded AST implementation and tool tests |
| FR-15 | Inspect outputs and suppress matched sensitive/unsafe content | Output-policy test with synthetic secret |
| FR-16 | Support deterministic demo and optional Ollama backend | Gateway browser flows; adapter request-shape test |
| FR-17 | Store scoped history, audits, policy and experiments in SQLite | Persistence/isolation/retention tests |
| FR-18 | Provide optional hashed accounts, roles and restricted service access | Login/role/token tests |
| FR-19 | Enforce CSRF, quotas, security headers and request limits | Security middleware and regression tests |
| FR-20 | Provide historical decision, language, detector and daily analytics | /api/analytics; browser verification |
| FR-21 | Let maintainers edit developer profiles and public CV links | developers.json, developer page route smoke test |

## 4. Policy behavior

Default thresholds are WARN 25, REVIEW 45, BLOCK 70, with recognized harmful content and sensitive data blocked independently. The lexical classifier may elevate an otherwise permitted request to review at score ≥65 when enabled. ALLOW/WARN may proceed; REVIEW/BLOCK stop. Disallowed tools stop regardless of input score. Output is released only after its own policy permits it. There is no automatic review override.

Legacy combined scores and risk bands remain for compatibility and are clearly distinct from the injection score and gateway decision.

## 5. Nonfunctional requirements

| ID | Requirement / measurable boundary |
|---|---|
| NFR-01 | Local baseline needs Python 3.10+, Flask and a browser; no GPU, LLM or API key |
| NFR-02 | ML installs separately and its method, training split/hash and limitations are recorded |
| NFR-03 | Inputs are bounded: 1 MiB body; 10,000 text characters; 50 batch items; documented gateway history/source limits |
| NFR-04 | Passwords are hashed; server credentials remain outside browser code; generated local secrets are excluded from distribution |
| NFR-05 | SQLite operations are scoped to the current logical owner; secret previews omitted; raw retention disabled by default |
| NFR-06 | Retention configurable from 1–365 days, default 30; 2,000 scans/workspace; cleanup on reads |
| NFR-07 | API failures return structured errors and meaningful HTTP status codes |
| NFR-08 | UI supports desktop/mobile, keyboard focus, original bilingual pages and reduced motion; operations pages currently English |
| NFR-09 | Evaluation reports exact/near overlap filtering, false positives/negatives, source hashes and real measured timings |
| NFR-10 | Integration tests verify stopped requests never invoke the backend and generated secrets are withheld |

No universal detection rate, fixed latency SLA or production availability claim is made. Latency varies with prompt length, decoding candidates, model initialization and hardware. API/model dependencies may need updates over time.

## 6. Data and architecture

SQLite entities: users, settings, scans, experiments, audit and quota limits. Scan/run IDs are random. Reports record engine/dataset fingerprints. See ARCHITECTURE.md for component and sequence diagrams; schema.sql is the initialized schema. The existing JSON corpora and rules remain versioned alongside the code.

## 7. Acceptance scenario

A student installs base requirements, starts app.py and scans benign/attack text. The result explains independent layers and stores a scoped scan. The student changes a policy, scans a hostile retrieved passage, compares rules/hybrid evaluation runs and exports results. A blocked gateway request does not reach its backend, while a permitted dry-run request completes. A synthetic secret in output is suppressed. An unauthorized calculator request stops. Authenticated analysts cannot write policy, and other workspaces cannot access scan/run IDs. Browser verification covers desktop/mobile navigation and the main flows.

## 8. Exclusions and future work

No guarantee of detecting all malicious/unsafe text; no deep semantic model, distributed workers, enterprise identity, tamper-evident logs, PDF/Word extraction, URL crawling, arbitrary tools or shared organization policy. A fresh human-labeled evaluation set and independent security review are prerequisites for stronger real-world claims. Live Ollama requires user-installed hardware/model/service and was not available for end-to-end build verification.
