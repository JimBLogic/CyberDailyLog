"use client";

import { useState } from "react";
import { clearLocalPreferences } from "@/lib/local-preferences";

export function ClearLocalPreferencesButton() {
  const [cleared, setCleared] = useState(false);

  function clearPreferences() {
    clearLocalPreferences();
    setCleared(true);
  }

  return (
    <div className="privacy-clear-control">
      <button type="button" onClick={clearPreferences}>
        Borrar preferencias locales / Clear local preferences
      </button>
      <p role="status" aria-live="polite">
        {cleared
          ? "Preferencias borradas de este navegador. / Preferences cleared from this browser."
          : "El botón elimina únicamente el idioma y la lista de seguimiento guardados por CyberDailyLog."}
      </p>
    </div>
  );
}
