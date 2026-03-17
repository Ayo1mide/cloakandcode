# Cloak and Code (v1.0) – Dev Notes

## Backend (FastAPI Proxy / Security Engine)
- Entry: `backend/main.py` (`uvicorn backend.main:app --reload --host 127.0.0.1 --port 8080`).
- Config: `backend/config.py` (env prefix `CLOAK_`; keys are **not** stored here).
- Key features:
  - Redaction via Presidio when available; regex fallback if not installed.
  - In-memory secret map per request; no disk writes.
  - Kill switch at `/toggle` (cloak on/off) keeps server alive; pass-through when off.
  - Multi-provider registry (OpenAI, Anthropic, Azure OpenAI, Gemini, Ollama) with pluggable auth and auto-detect from headers/model.
  - License/renewal loop with grace period and 20-requests/day cap when unlicensed.
  - **Strict BYOK**: API keys fetched from OS keychain at request time via `backend/keyvault.py`; not stored in files/env. Caller-supplied `Authorization`/`x-api-key` is forwarded as-is.
- Install deps: `pip install -r backend/requirements.txt`.

## Browser Extension (MV3)
- Files under `extension/`: `manifest.json`, `background.js`, `content.js`.
- Content script watches text areas on chat.openai.com/claude.ai; runs local NER where possible; warns on PII; on Enter it sends text to `http://127.0.0.1:8080/redact`, replaces with redacted text, then re-triggers send.
- Load as unpacked extension in Chrome/Edge.
- Build zip: `scripts/build_extension.ps1` → outputs `dist/cloakandcode-extension.zip`.

## Desktop Shell (Tauri, planned)
- Hosts the settings UI, license entry, and provider key vault (using OS keychain).
- Manages starting/stopping the Python sidecar.
- Not yet implemented in this repo; see `architecture.json` for responsibilities.

## Quick Start for AI Coder
- Provide `CLOAK_AND_CODE_PRD.md` and `WORKFLOW.md` as context.
- Initial prompt: “Generate FastAPI proxy that intercepts OpenAI chat completions and logs ‘Cloaking Active’.”

## Testing Aids
- `/redact` POST: returns redacted payload + secret map for quick checks.
- `/set-key` POST: dev-only (enable with `CLOAK_DEV_ENABLE_TEST_ENDPOINTS=1`) to write provider keys into OS keychain for local testing.
- See `docs/TESTING.md` for sample curl commands.

## Security Notes
- Bind to `127.0.0.1` only (config default).
- No request content persisted to disk; secret map wiped on process exit.
- Pass-through mode preserves IDE connectivity while disabling redaction.
