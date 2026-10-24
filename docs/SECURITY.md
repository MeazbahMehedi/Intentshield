# Security model and deployment notes

## Trust boundaries

The user prompt, conversation history and external sources are untrusted text. A detector score is evidence for a configurable policy, not authorization to execute arbitrary code. Retrieved material never receives system/developer authority. All sources are inspected before a model request. The model cannot request executable tools.

The gateway blocks REVIEW/BLOCK decisions before backend invocation and checks outputs before releasing text. WARN is permitted by design. Individual malicious prompts can still evade heuristic/lexical detection. The same rules cannot establish all harmful intent or guarantee safety in every language/context. This system should be one layer in an application's controls.

## Implemented controls

- No code/shell/browser/email execution from model output.
- Tools denied by default; only bounded arithmetic is available when permitted.
- Optional local accounts with Werkzeug password hashing; admin-only policy writes when authentication is enabled.
- Session-scoped data, redacted evidence and optional original-text retention.
- Stable generated local signing key or server environment secret; HttpOnly and SameSite cookies. Use Secure cookies with HTTPS hosting.
- Browser CSRF tokens and Origin host checks; restricted service-token bypass.
- Parameterized SQL; secret-bearing input previews omitted; CSV formula prefixes escaped.
- Request/text/batch/history/source/output limits, backend timeout and quotas.
- External URLs are not fetched from document content. The backend URL is a server-only setting.
- CSP, anti-framing, no-sniff, no-store and same-origin referrer headers.

## Local and hosted use

By default the server listens only on `127.0.0.1`. Do not expose the unauthenticated development server to a public network. For a controlled hosted installation, enable authentication, set a stable random PG_SECRET_KEY, restrict PG_API_TOKEN, use HTTPS/PG_COOKIE_SECURE=1 and a maintained WSGI/reverse-proxy configuration. SQLite files and instance keys are operational secrets; do not commit or bundle them. There is no default account.

PG_OLLAMA_URL is trusted administrator configuration. Requests disable inherited HTTP proxy settings. Point it only at a trusted model endpoint. Local-model text is forwarded only after input policy allows it. The dry-run backend sends nothing to a model.

Core interface fonts may be requested from Google Fonts; no prompt data is sent there. Remove those links for a completely offline appearance. The app uses system font fallbacks when fonts are unavailable.

## Known gaps

Pattern redaction can miss uncommon secrets. Raw retention explicitly stores original sensitive content. Educational-context masking and multilingual heuristics can produce false negatives/positives. Encoding inspection is deliberately bounded. Optional ML probabilities are uncalibrated and the small synthetic development corpus may not generalize.

Anonymous users can create fresh sessions; this quota is not global anti-abuse infrastructure. Authentication does not provide SSO, MFA, password reset, lockout, account lifecycle UI or organization-wide administration. Policy belongs to the current workspace, not all users; service access has a separate default policy. SQLite audit logs are editable by a local filesystem administrator and are not tamper-evident.

All clients must route requests through the gateway for its prevention controls to apply and supply relevant history/source text. A standalone scan cannot secure other apps. Output inspection uses the same limited detector family and can miss novel model-generated harm or exfiltration. Human review of stopped requests occurs outside the app; no bypass approval mechanism is included.

Use synthetic credentials and permitted test documents when demonstrating the project. More stringent production requirements need an independent security review and a different deployment architecture.

## GitHub profile boundary

The Developers page reads only public profile/repository data for two fixed source-code account names. Website requests cannot select an arbitrary account or destination URL and cannot edit profile or repository data. Server API requests target `api.github.com` only; redirects are disabled, pagination constructs fixed API paths, responses are size bounded and each account refresh has a 20-second request budget. Private repositories are excluded even if an optional token can access them.

`PG_GITHUB_TOKEN` is optional server-only configuration. It is not returned through HTML/JSON, sent to avatar hosts, or persisted in the public-data cache. Keep it out of source archives and GitHub commits. GitHub receives profile/repository requests from the server. Avatar images load directly from GitHub/`avatars.githubusercontent.com` in the browser with no-referrer policy; those hosts are explicitly permitted by CSP. Prompt, scan and gateway bodies are not sent by this integration.

Upstream strings render as text, external links accept HTTPS only, and new tabs use `noopener noreferrer`. Successful public metadata is cached separately from sensitive scan history. A local filesystem administrator can change source constants or the cache; read-only website behavior does not imply protection against server administrators. No GitHub write operation is implemented.
