# API reference

Run the server locally at `http://127.0.0.1:5000`. JSON request bodies must be objects. Invalid types, unknown policy fields, over-limit inputs and malformed JSON are rejected; prompts are never silently truncated.

## Authentication and CSRF

Browser requests use a session cookie plus `X-CSRF-Token`, read from the page's `meta[name="csrf-token"]`. HTML forms carry `csrf_token`. These are required even in local mode. Same-origin checks reject browser writes with a different Origin host. If authentication is enabled, sign in at `/login` first.

Automation can set `PG_API_TOKEN` server-side and send `Authorization: Bearer <token>` for the four service operations below. This bypasses browser CSRF checks only for those operations. It does not grant policy/evaluation/export/account administration. Never pass credentials in URLs.

## Service operations

| Method/path | Request | Result |
|---|---|---|
| POST `/api/scan` | `{"prompt":"Text"}` | `result`, redacted `history_entry`, workspace `stats` |
| POST `/api/batch` | `{"prompts":["Text","More text"]}` | `rows`, `count`; each row includes a scan ID and decision |
| POST `/api/documents/scan` | `{"content":"Text","source":"retrieval","name":"source.md"}` | `result`, boundary explanation, untrusted flag |
| POST `/api/gateway` | `{"prompt":"Text","backend":"demo"}` | Input/source/output evidence and backend/release flags |

Gateway optional fields:

```json
{
  "prompt": "Summarize these notes.",
  "backend": "demo",
  "history": ["Previous conversation turn"],
  "documents": [{"name": "notes.md", "content": "Source text"}],
  "tool": {"name": "calculator", "expression": "(12+8)/4"}
}
```

Supported source types: `document`, `email`, `web`, `retrieval`, `code`. Documents are supplied text; the server does not fetch URLs. Gateway documents always use an untrusted retrieval boundary. Optional history is caller-supplied context: clients must send relevant prior turns for multi-turn inspection.

## Scan report fields

`score`/`level` are compatible combined-pattern values. `injection_score` excludes safety-only findings. `harmful_content`, `sensitive_data`, `detectors`, `findings`, `source`, `normalization`, `language`, `ml`, `decision`, `latency_ms`, `engine_version`, `scan_id` expose the layers and evidence.

`findings[].evidence` is a redacted matched excerpt, not a claim of malicious intent. Variant findings refer to a decoded/normalized copy, so their offsets need not match original input offsets. Sensitive-data locations explicitly include the inspected variant. Original text SHA-256 is supplied for correlation; raw input is not returned in the report.

Gateway status: `completed`, `stopped`, `tool_denied`, `output_suppressed`, `backend_error`. Stop/suppression responses return HTTP 403. A backend error returns 502. `backend_called: true` means a successful backend response was received, including the explicitly labeled demo backend. Backend errors may occur after a network request was attempted. Blocked requests set it false and are tested never to invoke the adapter.

`output` appears only after release. Calculator results appear only for successfully completed requests. No model tool-call field is interpreted or executed.

## Session operations

| Method/path | Purpose |
|---|---|
| GET/POST `/api/policy` | Read policy / admin-only save when authentication enabled |
| POST `/api/evaluations` | Run split `development|holdout|robustness|test`, mode `rules|hybrid|ml`, boolean `clean` |
| GET `/api/evaluations` | Latest 30 scoped run summaries |
| GET `/api/evaluations/<id>/export?format=csv|json` | Download results |
| GET `/api/evaluations/compare?left=<id>&right=<id>` | Right-minus-left metric deltas; same dataset hash/filter required |
| GET `/api/datasets/audit` | Schema validation, exact and near cross-split overlap audit |
| GET `/api/analytics` | Persistent daily trends, decisions, detector/language counts and latency |
| GET `/api/dashboard?range=day|week|month|all` | Legacy dashboard-compatible chart data |
| GET `/api/export?format=csv|json` | Scoped retained scans; CSV cells neutralize formula prefixes |
| POST `/api/seed-demo` | Add clearly marked demonstration scans |
| POST `/api/clear-session` | Delete workspace scan history; keeps login, policy and audit metadata |
| GET `/health` | Unauthenticated `ok` liveness response |

Policy keys: `warn`, `review`, `block` (strictly increasing integers, 1–100); `block_harmful`, `block_sensitive`, `ml_enabled`, `retain_prompts` (booleans); `retention_days` (1–365); `tools` (empty or `["calculator"]`). Omitted keys use defaults.

## Limits and failures

- Request body: 1 MiB. Prompt/source: 10,000 characters.
- Batch: at most 50 prompts. No automatic truncation.
- Gateway: at most 12 history turns, each ≤2,000 characters; combined prompt/history ≤10,000 characters; at most 5 sources, each ≤10,000 characters.
- Browser text loader: ≤100 KB and ≤10,000 decoded characters.
- Calculator: ≤100 characters, maximum expression depth 12, absolute intermediate/result value ≤10^12. Only numeric constants, unary ± and binary + − × ÷.
- Rate: 60 writes per minute per workspace by default, set with `PG_RATE_LIMIT`. Login attempts are counted by remote address. This is a local prototype quota, not distributed abuse prevention.
- Ollama: 45-second timeout, 1 MiB response byte cap, 10,000-character output inspection limit, 256 predicted-token request option.
- Errors use JSON `error` for API requests: 400 invalid data, 401 unauthenticated, 403 denied/CSRF/policy, 404 missing or other-workspace record, 413 too large, 429 quota, 502 backend failure.
