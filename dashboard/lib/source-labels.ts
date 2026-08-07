export const SOURCE_LABELS: Record<string, string> = {
  cisa_kev: "CISA KEV",
  nvd: "NVD",
  github_advisories: "GitHub Advisories",
  github_releases: "Defensive releases",
  rss_krebs: "Krebs on Security",
  rss_sans_isc: "SANS ISC",
  hacker_news: "Hacker News",
  epss: "FIRST EPSS",
  official_nvd_backup: "NVD API 2.0",
  official_cisa_backup: "CISA KEV JSON",
  official_epss_backup: "FIRST EPSS API",
};

export const SOURCE_SHORT_LABELS: Record<string, string> = {
  cisa_kev: "CISA",
  nvd: "NVD",
  github_advisories: "GitHub",
  github_releases: "Releases",
  rss_krebs: "Krebs",
  rss_sans_isc: "SANS ISC",
  hacker_news: "HN",
  epss: "FIRST",
  official_nvd_backup: "NVD",
  official_cisa_backup: "CISA",
  official_epss_backup: "EPSS",
};

export const SOURCE_URLS: Record<string, string> = {
  cisa_kev: "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
  nvd: "https://nvd.nist.gov/",
  github_advisories: "https://github.com/advisories",
  github_releases: "https://github.com/SigmaHQ/sigma/releases",
  rss_krebs: "https://krebsonsecurity.com/",
  rss_sans_isc: "https://isc.sans.edu/",
  hacker_news: "https://news.ycombinator.com/",
  epss: "https://www.first.org/epss/",
  official_nvd_backup: "https://nvd.nist.gov/developers/vulnerabilities",
  official_cisa_backup: "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
  official_epss_backup: "https://www.first.org/epss/data",
};

/** Expected publication cadence used to judge freshness, not source quality. */
export const SOURCE_EXPECTED_INTERVAL_MINUTES: Record<string, number> = {
  cisa_kev: 1_440,
  nvd: 1_440,
  github_advisories: 1_440,
  github_releases: 1_440,
  rss_krebs: 1_440,
  rss_sans_isc: 1_440,
  hacker_news: 1_440,
  epss: 1_440,
  official_nvd_backup: 120,
  official_cisa_backup: 120,
  official_epss_backup: 120,
};

export function sourceExpectedIntervalMs(source: string) {
  return (SOURCE_EXPECTED_INTERVAL_MINUTES[source] ?? 1_440) * 60_000;
}

export type SourceTrustLane = "evidence" | "expert" | "community";
export type SourceProvenance =
  | "government"
  | "advisory_registry"
  | "probability_model"
  | "first_party"
  | "specialist"
  | "community";

/** Describes how CyberDailyLog uses a source; it is not a universal score. */
export const SOURCE_PROFILES: Record<
  string,
  { lane: SourceTrustLane; provenance: SourceProvenance }
> = {
  cisa_kev: { lane: "evidence", provenance: "government" },
  nvd: { lane: "evidence", provenance: "government" },
  github_advisories: { lane: "evidence", provenance: "advisory_registry" },
  epss: { lane: "evidence", provenance: "probability_model" },
  github_releases: { lane: "expert", provenance: "first_party" },
  rss_krebs: { lane: "expert", provenance: "specialist" },
  rss_sans_isc: { lane: "expert", provenance: "specialist" },
  hacker_news: { lane: "community", provenance: "community" },
  official_nvd_backup: { lane: "evidence", provenance: "government" },
  official_cisa_backup: { lane: "evidence", provenance: "government" },
  official_epss_backup: { lane: "evidence", provenance: "probability_model" },
};
