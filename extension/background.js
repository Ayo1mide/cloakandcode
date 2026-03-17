chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.set({ cloakEnabled: true });
});

chrome.action.onClicked.addListener(async (tab) => {
  const current = (await chrome.storage.local.get("cloakEnabled")).cloakEnabled ?? true;
  const next = !current;
  await chrome.storage.local.set({ cloakEnabled: next });
  chrome.action.setBadgeText({ text: next ? "ON" : "OFF" });
  chrome.action.setBadgeBackgroundColor({ color: next ? "#00E6FF" : "#6B7280" });
});
