# Testing the Proxy and Keychain Helpers

## 1) Redaction sanity check
```bash
curl -X POST http://127.0.0.1:8080/redact \
  -H "Content-Type: application/json" \
  -d '{"text": "My email is jane@example.com and my key is sk-abc1234567890"}'
```
Expected: response with `secret_map` containing detected secrets and `redacted.messages[0].content` with tokens.

## 2) Store a provider key in the OS keychain (dev-only)
Enable test endpoints:
- Windows/Powershell: `$env:CLOAK_DEV_ENABLE_TEST_ENDPOINTS=1`
- macOS/Linux: `export CLOAK_DEV_ENABLE_TEST_ENDPOINTS=1`

Then:
```bash
curl -X POST "http://127.0.0.1:8080/set-key?provider=openai&key=sk-abc123"
```
Keys are saved via OS keychain and only pulled into memory per request.

## 3) Proxy end-to-end (using stored key)
```bash
curl -X POST http://127.0.0.1:8080/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"Ping"}]}'
```
If no Authorization header is supplied, proxy will inject the key from the vault (if present) for the detected provider.
```
