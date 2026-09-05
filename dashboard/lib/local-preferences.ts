export const LANGUAGE_STORAGE_KEY = "cyberdailylog-language";
export const WATCHLIST_STORAGE_KEY = "cyberdailylog-watchlist";

export type LanguagePreference = "en" | "es";

const WATCHLIST_ENTRY = /^[A-Za-z0-9._:-]{1,160}$/;
const MAX_WATCHLIST_ITEMS = 500;

function localStorageOrNull() {
  if (typeof window === "undefined") return null;
  try {
    return window.localStorage;
  } catch {
    return null;
  }
}

export function readLanguagePreference(): LanguagePreference | null {
  try {
    const value = localStorageOrNull()?.getItem(LANGUAGE_STORAGE_KEY);
    return value === "en" || value === "es" ? value : null;
  } catch {
    return null;
  }
}

export function readWatchlistPreference(): string[] {
  try {
    const value = localStorageOrNull()?.getItem(WATCHLIST_STORAGE_KEY);
    if (!value) return [];
    const parsed: unknown = JSON.parse(value);
    if (!Array.isArray(parsed)) return [];
    return parsed
      .filter(
        (item): item is string =>
          typeof item === "string" && WATCHLIST_ENTRY.test(item),
      )
      .slice(0, MAX_WATCHLIST_ITEMS);
  } catch {
    return [];
  }
}

export function saveLanguagePreference(language: LanguagePreference) {
  try {
    localStorageOrNull()?.setItem(LANGUAGE_STORAGE_KEY, language);
  } catch {
    // The interface remains usable if browser storage is unavailable.
  }
}

export function saveWatchlistPreference(ids: Iterable<string>) {
  const safeIds = [...new Set(ids)]
    .filter((item) => WATCHLIST_ENTRY.test(item))
    .slice(0, MAX_WATCHLIST_ITEMS);
  try {
    localStorageOrNull()?.setItem(
      WATCHLIST_STORAGE_KEY,
      JSON.stringify(safeIds),
    );
  } catch {
    // The interface remains usable if browser storage is unavailable.
  }
}

export function clearLocalPreferences() {
  const storage = localStorageOrNull();
  if (!storage) return;
  try {
    storage.removeItem(LANGUAGE_STORAGE_KEY);
    storage.removeItem(WATCHLIST_STORAGE_KEY);
  } catch {
    // Nothing else is stored by CyberDailyLog.
  }
}
