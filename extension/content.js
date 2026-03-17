const WARNING_COLOR = "#f59e0b";
const WARNING_ID = "cloak-and-code-warning";
let modelPromise = null;
const REDACT_ENDPOINT = "http://127.0.0.1:8080/redact";

async function loadModel() {
  if (modelPromise) return modelPromise;
  modelPromise = import("https://cdn.jsdelivr.net/npm/@xenova/transformers@2.17.1")
    .then(async (tf) => {
      const pipe = await tf.pipeline("token-classification", "Xenova/bert-base-uncased-finetuned-ner");
      return pipe;
    })
    .catch((err) => {
      console.warn("Transformers.js unavailable, falling back to regex detection", err);
      return null;
    });
  return modelPromise;
}

async function isCloakEnabled() {
  const { cloakEnabled } = await chrome.storage.local.get("cloakEnabled");
  return cloakEnabled !== false;
}

function injectWarning(el, message) {
  let banner = document.getElementById(WARNING_ID);
  if (!banner) {
    banner = document.createElement("div");
    banner.id = WARNING_ID;
    banner.style.position = "absolute";
    banner.style.bottom = "8px";
    banner.style.right = "8px";
    banner.style.padding = "6px 10px";
    banner.style.background = WARNING_COLOR;
    banner.style.color = "#111827";
    banner.style.fontSize = "12px";
    banner.style.borderRadius = "6px";
    banner.style.zIndex = "9999";
    banner.style.boxShadow = "0 2px 6px rgba(0,0,0,0.15)";
    el.parentElement.appendChild(banner);
  }
  banner.textContent = message;
}

function removeWarning() {
  const banner = document.getElementById(WARNING_ID);
  if (banner && banner.parentElement) {
    banner.parentElement.removeChild(banner);
  }
}

function simpleDetectPII(text) {
  const patterns = [
    /(sk-[A-Za-z0-9]{20,})/, // OpenAI-style keys
    /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}/, // emails
    /\\b\\d{3}-\\d{2}-\\d{4}\\b/ // SSN-like
  ];
  return patterns.some((p) => p.test(text));
}

async function detectPII(text) {
  const ner = await loadModel();
  if (ner) {
    try {
      const entities = await ner(text, { aggregation_strategy: "simple" });
      return entities && entities.length > 0;
    } catch (e) {
      return simpleDetectPII(text);
    }
  }
  return simpleDetectPII(text);
}

async function cleanViaProxy(text) {
  try {
    const res = await fetch(REDACT_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });
    if (!res.ok) return text;
    const data = await res.json();
    const redacted = data?.redacted?.messages?.[0]?.content || text;
    return redacted;
  } catch (e) {
    return text;
  }
}

async function attachWatchers() {
  const inputs = document.querySelectorAll("textarea, [contenteditable='true']");
  inputs.forEach((input) => {
    input.removeEventListener("input", input._cloakHandler || (() => {}));
    input.removeEventListener("keydown", input._cloakSubmitHandler || (() => {}));
    const handler = async () => {
      if (!(await isCloakEnabled())) {
        removeWarning();
        return;
      }
      const text = input.value || input.innerText || "";
      if (await detectPII(text)) {
        injectWarning(input, "PII/secret detected. Cloak before sending.");
      } else {
        removeWarning();
      }
    };
    const submitHandler = async (ev) => {
      if (!(await isCloakEnabled())) return;
      if (ev.key === "Enter" && !ev.shiftKey && !ev.metaKey && !ev.ctrlKey) {
        ev.preventDefault();
        const text = input.value || input.innerText || "";
        const cleaned = await cleanViaProxy(text);
        if (input.value !== undefined) input.value = cleaned;
        else input.innerText = cleaned;
        input.dispatchEvent(new Event("input", { bubbles: true }));
        // Re-trigger Enter so the host app sends the message
        const enterEvent = new KeyboardEvent("keydown", { key: "Enter", bubbles: true });
        input.dispatchEvent(enterEvent);
      }
    };
    input._cloakHandler = handler;
    input._cloakSubmitHandler = submitHandler;
    input.addEventListener("input", handler);
    input.addEventListener("keydown", submitHandler, true);
  });
}

const observer = new MutationObserver(() => attachWatchers());
observer.observe(document.body, { childList: true, subtree: true });
attachWatchers();
