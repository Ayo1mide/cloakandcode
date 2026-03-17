Project Scope: Cloak and Code (v1.0)
1. Project Overview
Cloak and Code is a local-first privacy shield for developers using AI tools (ChatGPT, Cursor, VS Code). It intercepts outgoing AI requests, redacts sensitive information (API keys, PII, secrets) locally using Machine Learning, and replaces them with placeholders. It then restores the original data in the AI's response.
Goal: Zero data leakage to the cloud.
2. Technical Architecture
The system consists of three integrated components:
 * Local Proxy (Python/FastAPI): Intercepts traffic from desktop apps (Cursor/VS Code).
 * Browser Extension (Manifest V3): Intercepts traffic from web-based AI chats.
 * Redaction Engine: Uses Microsoft Presidio (Python) and Transformers.js (JS) for local inference.
3. Core Features & Requirements
A. The "Cloak" Proxy (Desktop)
 * Intercept: Run a FastAPI server on http://localhost:8080.
 * Routing: Redirect traffic to https://api.openai.com/v1 or https://api.anthropic.com.
 * Logic: * Parse JSON request bodies.
 * Scan messages content for secrets using Microsoft Presidio.
 * Store a temporary "Secret Map" in local memory (RAM).
 * Replace secrets with tokens (e.g., [SECRET_API_KEY_1]).
 * Response Handling: When the AI responds, replace the tokens with the original values from the Secret Map before the IDE displays them.
 * Multi-Provider Ready: The proxy keeps a pluggable provider registry (base_url + auth header template) so additional AI APIs (e.g., Azure OpenAI, Google Gemini, local/Ollama endpoints) can be added without changing the redaction flow.
B. The Browser Extension (Web)
 * Content Script: Monitors text areas on chat.openai.com and claude.ai.
 * Keystroke Guard: Warns the user before they hit send if PII is detected.
 * Local Inference: Use Transformers.js with a small quantized model (like distilbert-base-uncased) to run NER (Named Entity Recognition) entirely in the browser.
C. The "Kill Switch" & Auto-Start
 * System Tray: Use pystray to keep the proxy running in the background.
 * On/Off Toggle: Allow users to disable "Cloaking" with one click.
D. The "Global Kill Switch" (Section 3.4)
 * Pass-Through Mode: When the toggle is set to OFF, the FastAPI proxy must not stop the server (to avoid breaking the connection to Cursor/VS Code). It must simply forward the raw JSON request to OpenAI/Anthropic without running the redact_content() function.
 * UI Feedback: The System Tray icon (Tauri) must change from Neon Cyan (Active) to Stealth Grey (Inactive) to provide instant visual confirmation.
4. Monetization & Licensing
 * License Check: On startup, the app makes one GET request to https://api.cloakandcode.ai/verify?key=USER_KEY.
 * Local Limit: If the key is invalid, limit the proxy to 20 requests per day.
 * Lemon Squeezy Integration: Link the "Upgrade" button to a Lemon Squeezy checkout URL.
4.1 The "Smart Renewal" Logic
 * Silent Sync: On every app launch (or every 24h), the Python backend pings the Lemon Squeezy API using the cached license_key and machine_id.
 * Grace Period: If the API returns past_due, the app enters a 3-day "Grace Period" where it stays active but shows a yellow warning icon.
 * Auto-Resume: If the status changes from expired to active, the app must instantly unlock without requiring the user to re-type the key.
5. Technology Stack
 * Backend: Python 3.10+, FastAPI, Uvicorn.
 * Security Engine: presidio-analyzer, presidio-anonymizer, spacy.
 * Extension: JavaScript (ES6+), Chrome Manifest V3.
 * Packaging: PyInstaller (to turn the Python script into a .exe or .app for users).
6. Security & Privacy Constraints
 * No Logging: The proxy must NOT write request content to any disk files.
 * Memory Only: The "Secret Map" must be wiped when the session ends.
 * Localhost Only: The server must bind only to 127.0.0.1 to prevent external network access.
How to start the build in Cursor:
 * Open an empty folder.
 * Create a file named app.py.
 * Type: "Based on the CLOAK_AND_CODE_PRD.md, generate the initial FastAPI proxy that can intercept a standard OpenAI chat completion request and print 'Cloaking Active' to the terminal."
