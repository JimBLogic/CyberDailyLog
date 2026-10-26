export const LANGUAGE_STORAGE_KEY = "cyberdailylog-language";
export const THEME_STORAGE_KEY = "cyberdailylog-theme";
export const WATCHLIST_STORAGE_KEY = "cyberdailylog-watchlist";

export type ThemePreference = "light" | "dark";
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
  memoryTheme = "light";
  if (typeof document !== "undefined") document.documentElement.dataset.theme = "light";
  if (typeof window !== "undefined") window.dispatchEvent(new Event(THEME_EVENT));
  if (!storage) return;
  try {
    storage.removeItem(LANGUAGE_STORAGE_KEY);
    storage.removeItem(WATCHLIST_STORAGE_KEY);
    storage.removeItem(THEME_STORAGE_KEY);
  } catch {
    // Nothing else is stored by CyberDailyLog.
  }
}


// Run before first paint; untrusted storage values are never inserted into HTML.
export const THEME_BOOTSTRAP_SCRIPT = "(function(){try{var t=window.localStorage.getItem('cyberdailylog-theme');document.documentElement.dataset.theme=t==='dark'?'dark':'light'}catch{}})()";
const THEME_EVENT = "cyberdailylog-theme-change";
let memoryTheme: ThemePreference | null = null;

export function readThemePreference(): ThemePreference | null {
  try {
    const value = localStorageOrNull()?.getItem(THEME_STORAGE_KEY);
    return value === "dark" || value === "light" ? value : null;
  } catch { return null; }
}

export function themeSnapshot(): ThemePreference {
  return memoryTheme ?? readThemePreference() ?? "light";
}

export function saveThemePreference(theme: ThemePreference) {
  memoryTheme = theme;
  if (typeof document !== "undefined") document.documentElement.dataset.theme = theme;
  try { localStorageOrNull()?.setItem(THEME_STORAGE_KEY, theme); } catch {
    // A blocked storage API must not prevent switching during this visit.
  }
  if (typeof window !== "undefined") window.dispatchEvent(new Event(THEME_EVENT));
}

export function subscribeThemePreference(listener: () => void) {
  const onStorage = (event: StorageEvent) => {
    if (event.key !== THEME_STORAGE_KEY && event.key !== null) return;
    memoryTheme = null;
    document.documentElement.dataset.theme = themeSnapshot();
    listener();
  };
  window.addEventListener(THEME_EVENT, listener);
  window.addEventListener("storage", onStorage);
  return () => {
    window.removeEventListener(THEME_EVENT, listener);
    window.removeEventListener("storage", onStorage);
  };
}
