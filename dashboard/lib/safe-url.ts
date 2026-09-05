/** Only absolute web links may cross the feed-to-interface boundary. */
export function safeWebUrl(value: unknown, fallback = "") {
  if (typeof value !== "string") return fallback;
  try {
    const url = new URL(value.trim());
    if (!["https:", "http:"].includes(url.protocol) || url.username || url.password) return fallback;
    return url.href;
  } catch {
    return fallback;
  }
}
