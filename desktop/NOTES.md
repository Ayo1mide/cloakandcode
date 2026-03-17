# Desktop Shell (Tauri/Rust) Plan

- Responsibilities:
  - Secure vault UI: collect API keys per provider (openai, anthropic, gemini, perplexity) and store via OS keychain (aligns with backend/keyvault.py service name `CloakAndCode`).
  - License UI: capture license key and display status/grace warnings (yellow icon for past_due).
  - Global toggle: turn cloak on/off; call backend `/toggle` endpoint; update tray icon (Neon Cyan active, Stealth Grey inactive).
  - Process manager: start/stop the Python sidecar (uvicorn) at app launch/quit; watch for crashes and restart.
- Suggested stack:
  - Tauri + React frontend.
  - tauri-plugin-stronghold or `keyring-rs` for keychain.
  - Command to start proxy: `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8080`.
- IPC sketch:
  - `set_key(provider, key)` -> writes to keychain.
  - `get_status()` -> calls `/health`.
  - `toggle(enabled)` -> calls `/toggle`.
  - `run_proxy()` -> spawns sidecar; `stop_proxy()` -> kills process.
- Build order:
  1) Scaffold Tauri app in `desktop/`.
  2) Wire key entry form to keychain writes matching backend names.
  3) Add toggle + status polling.
  4) Add license entry + status badges (green/amber/red).
