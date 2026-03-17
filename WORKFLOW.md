# Cloak and Code – User Workflow (v1.0)

## 1) Installation & First Launch
- Download and run the packaged app (PyInstaller build).
- On first start, the FastAPI proxy binds to `127.0.0.1:8080` and opens a small tray UI.
- Enter your license key; the app verifies it with Lemon Squeezy and caches `license_key` + `machine_id` locally (no request content is logged).

## 2) Daily Use – Desktop Proxy (Cursor / VS Code)
- IDE is configured to point AI traffic to `http://127.0.0.1:8080`.
- Provider registry supports OpenAI, Anthropic, and additional endpoints (e.g., Azure OpenAI, Gemini, local/Ollama); selection is config-based, redaction flow stays identical.
- When you send a prompt, the proxy:
  1. Parses the JSON request.
  2. Detects secrets/PII with Presidio.
  3. Replaces them with in-memory tokens and forwards the scrubbed request to OpenAI/Anthropic.
  4. Receives the AI response and restores the originals before returning it to the IDE.
- Tray icon shows Neon Cyan when cloaking is active.

## 3) Browser Extension (chat.openai.com / claude.ai)
- The MV3 extension injects a content script into chat text areas.
- As you type, a lightweight Transformers.js NER model runs locally:
  - If PII/secrets are detected, you get an inline warning before sending.
- Requests still flow through the site normally; detection is local and does not alter the network path.

## 4) Global Kill Switch (Pass-Through Mode)
- Toggle from the tray:
  - ON → Redaction enabled (Neon Cyan).
  - OFF → Proxy stays running but forwards raw JSON without `redact_content()` (Stealth Grey icon). Keeps IDE connectivity intact.

## 5) Licensing, Payment, and Renewal
- Activation: Initial check hits `https://api.cloakandcode.ai/verify?key=USER_KEY` (plus Lemon Squeezy license API).
- Smart Renewal (24h or on launch):
  - Calls Lemon Squeezy with cached `license_key` + `machine_id`.
  - `past_due` → 3-day Grace Period; app remains active, icon shows Yellow warning.
  - If status returns to `active`, full functionality auto-resumes—no retyping the key.
- Upgrade path: “Upgrade”/“Manage Billing” opens the Lemon Squeezy checkout URL.
- Invalid/expired with Grace exhausted → fallback to 20 requests/day local limit.

## 6) Privacy & Security Guarantees
- Localhost-only binding; no external access.
- Secret Map lives only in RAM and is wiped on exit.
- No request bodies are written to disk.

## 7) Quick Start Script for AI Coder (Cursor)
- Create `app.py`.
- Prompt: “Based on CLOAK_AND_CODE_PRD.md and WORKFLOW.md, generate the initial FastAPI proxy that intercepts a standard OpenAI chat completion request and logs ‘Cloaking Active’ to the terminal.”
