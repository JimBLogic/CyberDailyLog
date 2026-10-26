"use client";

import { useEffect, useSyncExternalStore } from "react";
import { saveThemePreference, subscribeThemePreference, themeSnapshot } from "@/lib/local-preferences";

const serverTheme = () => "light" as const;

export function ThemeToggle({ language = "es" }: { language?: "es" | "en" }) {
  const theme = useSyncExternalStore(subscribeThemePreference, themeSnapshot, serverTheme);
  const dark = theme === "dark";
  const label = language === "es"
    ? (dark ? "Activar modo claro" : "Activar modo oscuro")
    : (dark ? "Switch to light mode" : "Switch to dark mode");
  useEffect(() => { document.documentElement.dataset.theme = theme; }, [theme]);
  return <button type="button" className="theme-toggle" aria-label={label} title={label}
    aria-pressed={dark} onClick={() => saveThemePreference(dark ? "light" : "dark")}>
    <svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      {dark ? <><circle cx="12" cy="12" r="4" /><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5" /></> : <path d="M20.5 13.5A8.5 8.5 0 0 1 10.5 3.5a8.5 8.5 0 1 0 10 10Z" />}
    </svg>
    <span>{language === "es" ? (dark ? "Oscuro" : "Claro") : (dark ? "Dark" : "Light")}</span>
  </button>;
}
