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

/** CISA notes can contain several URLs and human labels in one field. */
export function referenceUrls(values: unknown[]) {
  const links: string[] = [];
  for (const value of values) {
    if (typeof value !== "string" || /^\s*(javascript|data|file|vbscript):/i.test(value)) continue;
    const normalized = value.replace(/%20;%20/gi, " ; ");
    for (const token of normalized.match(/https?:\/\/[^\s<>"']+/gi) ?? []) {
      const url = safeWebUrl(token.replace(/[;,.]+$/, ""));
      if (url && !links.includes(url)) links.push(url);
    }
  }
  return links.slice(0, 6);
}
