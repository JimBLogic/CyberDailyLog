export const ESSENTIAL_SERVER_HOSTS = Object.freeze([
  "api.first.org",
  "cdn.jsdelivr.net",
  "raw.githubusercontent.com",
  "services.nvd.nist.gov",
  "www.cisa.gov",
] as const);

const essentialServerHosts = new Set<string>(ESSENTIAL_SERVER_HOSTS);

export function essentialServerUrl(input: string | URL) {
  const url = input instanceof URL ? input : new URL(input);
  if (url.protocol !== "https:" || !essentialServerHosts.has(url.hostname)) {
    throw new Error(`Blocked outbound host: ${url.hostname}`);
  }
  return url;
}
