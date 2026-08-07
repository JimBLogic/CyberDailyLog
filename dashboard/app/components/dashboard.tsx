"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  SOURCE_PROFILES,
  SOURCE_SHORT_LABELS,
  SOURCE_URLS,
} from "@/lib/source-labels";
import type {
  SourceProvenance,
  SourceTrustLane,
} from "@/lib/source-labels";
import type {
  DashboardData,
  HistoryPoint,
  Severity,
  SourceHealth,
  Vulnerability,
} from "@/lib/types";

type View =
  | "overview"
  | "vulnerabilities"
  | "sources"
  | "methodology"
  | "engineering";
type Language = "en" | "es";

const COPY = {
  en: {
    overview: "Today",
    vulnerabilities: "Briefing",
    sources: "Sources",
    methodology: "Methodology",
    engineering: "Project",
    morning: "Daily threat brief",
    eyebrow: "Daily Blue Team intelligence",
    heroA: "See the threat.",
    heroB: "Act with confidence.",
    heroText:
      "CyberDailyLog gathers trusted sources, separates evidence from noise and shows defenders what to review first.",
    openBrief: "View priorities",
    how: "How it works",
    operational: "From source to action",
    collect: "Collect",
    normalize: "Normalize",
    score: "Score",
    publish: "Publish",
    live: "Live",
    updated: "Updated",
    coverage: "24-hour coverage",
    topPriority: "Top priority",
    why: "Why it matters",
    action: "Defensive action",
    primarySource: "Open primary source",
    noConfirmed: "No confirmed exploitation",
    notKev: "Not in CISA KEV",
    assessed: "assessed",
    above: "above threshold",
    core: "Core sources",
    optional: "Optional sources",
    healthy: "healthy",
    healthySingle: "healthy",
    riskDistribution: "Risk distribution",
    total: "of security items",
    sourceHealth: "Source health",
    sourceFreshness: "Status from the latest collection run",
    historical: "Eight-day signal",
    historicalText:
      "Daily volume, high-impact items and pipeline status from the repository archive.",
    humanContext: "Analyst context",
    community: "Community pulse",
    verify: "Treat community interest as a lead, not verified intelligence.",
    readSource: "Read at source",
    openDiscussion: "Open discussion",
    allIntel: "All ranked intelligence",
    intelIntro:
      "Search and triage the bounded dataset published by the latest pipeline run.",
    search: "Search CVE, product or description",
    allSeverities: "All severities",
    attentionOnly: "Exploitation / KEV only",
    watchlistOnly: "Watchlist only",
    priority: "Priority",
    newest: "Newest",
    cvss: "CVSS",
    exportJson: "Export JSON",
    exportCsv: "Export CSV",
    showing: "Showing",
    items: "items",
    empty: "No intelligence items match these filters.",
    watch: "Add to watchlist",
    unwatch: "Remove from watchlist",
    details: "Open details",
    sourceOperations: "Collector operations",
    sourceIntro:
      "Inspect trust tier, latency, acceptance and failure state for every source in the run.",
    required: "Core",
    optionalLabel: "Optional",
    received: "Received",
    accepted: "Accepted",
    latency: "Latency",
    status: "Status",
    coverageLimits: "Coverage & limits",
    coverageLimitsText:
      "See what this run can support, which sources need attention and how every signal is used.",
    whatWeSee: "What we can see",
    currentSource: "source reported recently and without collection errors.",
    currentSources: "sources reported recently and without collection errors.",
    intelligenceGaps: "Intelligence gaps",
    noGaps: "No source gaps detected in this run.",
    gapSource: "source is late, degraded, unavailable or only using test data.",
    gapSources: "sources are late, degraded, unavailable or only using test data.",
    coverageCaveat:
      "A healthy collector confirms access to that source, not complete coverage of the internet.",
    fresh: "Recent",
    late: "Needs update",
    unavailableSource: "No reliable timestamp",
    sourceUse: "How we use it",
    provenanceGovernment: "Official public body",
    provenanceAdvisoryRegistry: "Coordinated advisory registry",
    provenanceProbabilityModel: "Independent probability model",
    provenanceFirstParty: "First-party release",
    provenanceSpecialist: "Specialist publisher",
    provenanceCommunity: "Community discussion",
    resiliencePath: "Resilient delivery path",
    resilienceText:
      "The dashboard changes route without hiding which source is currently in use.",
    used: "In use",
    available: "Available",
    skipped: "On standby",
    unavailableRoute: "Unavailable",
    methodTitle: "Transparent by design",
    methodIntro:
      "A reproducible collection and curation pipeline, with claims, context and community interest kept in separate trust lanes.",
    collection: "1. Collect",
    collectionText:
      "CISA KEV, NVD, GitHub Advisories and FIRST EPSS provide structured evidence. Curated RSS and Hacker News add explicitly labelled context.",
    normalization: "2. Normalize",
    normalizationText:
      "Records are mapped to a stable schema, deduplicated and correlated without executing proof-of-concept code or downloading malware.",
    scoring: "3. Score",
    scoringText:
      "Deterministic weights prioritize exploitation, KEV, ransomware use, CVSS, EPSS, attack conditions and defensive relevance.",
    publication: "4. Publish",
    publicationText:
      "The human brief, complete evidence, compact API feed, source health and historical archive are validated before publication.",
    trustBoundaries: "Trust boundaries",
    evidence: "Evidence",
    evidenceText: "CVE, KEV, EPSS and official advisories.",
    expert: "Expert context",
    expertText: "Short, attributed excerpts from allowlisted publishers.",
    communityLane: "Community signal",
    communityText: "Engagement is never presented as verified risk.",
    portable: "One project, two useful surfaces",
    portableText:
      "The repository remains independently runnable. Its generated JSON powers this backend, while the dashboard code and data contract return to the repository for local or alternative hosting.",
    repo: "Open repository",
    runLocal: "Standalone instructions",
    dataContract: "Inspect JSON contract",
    close: "Close",
    references: "References",
    reasons: "Priority reasons",
    actions: "Recommended actions",
    published: "Published",
    fetched: "Dashboard fetch",
    dataMode: "Data source",
    liveRepo: "Live repository data",
    snapshot: "Repository snapshot fallback",
    refreshing: "Refreshing…",
    refresh: "Refresh data",
    refreshFailed: "Live refresh failed; the verified snapshot remains visible.",
    refreshed: "Sources checked and refreshed.",
    fallbackRetained:
      "The primary report is unavailable. A labelled backup remains visible.",
    primaryNavigation: "Primary navigation",
    language: "Language",
    runSummary: "Run summary",
    sort: "Sort intelligence",
    critical: "Critical",
    high: "High",
    medium: "Medium",
    low: "Low",
    unknown: "Unclassified",
    exploited: "Exploitation reported",
    ransomware: "Ransomware linked",
    yes: "Yes",
    no: "No",
    comments: "comments",
    points: "points",
    reference: "Reference",
    totalCollectorTime: "total collector time",
    immediateAttention: "Immediate attention",
    noImmediate:
      "No item in this run has confirmed exploitation, CISA KEV or ransomware use.",
    immediateCount:
      "items require immediate review because they include exploitation, KEV or ransomware signals.",
    scoreLabel: "Priority score · 0–10",
    scoreFormula:
      "CISA KEV +50 · confirmed exploitation +40 · ransomware +25 · critical CVSS +20 · very high EPSS +25 · official source +5",
    statusOperational: "Operational",
    statusDegraded: "Degraded",
    statusHealthy: "Healthy",
    statusFailed: "Failed",
    statusFixture: "Test fixture",
    statusUnknown: "Unknown",
    signalDesk: "Signal desk",
    signalDeskTitle: "More than CVEs: today’s analyst reading",
    signalDeskText:
      "Operational diaries and community leads collected in the same daily run, clearly separated by evidence level.",
    analystBriefs: "Analyst & publisher briefings",
    communitySignals: "Community signals",
    originalSource: "Original source content",
    originalSourceNote:
      "Titles and excerpts remain in the publisher’s original language to preserve accuracy.",
    viewSignal: "Open signal",
    interviewEyebrow: "Interview-ready proof of work",
    interviewTitle: "I did not just follow the news. I built the workflow.",
    interviewQuote:
      "When asked where I stay current, CyberDailyLog is my answer: a reproducible Blue Team pipeline that collects, validates, prioritizes and publishes a daily briefing.",
    proofProblem: "Problem",
    proofProblemText:
      "Security information is fragmented, noisy and difficult to turn into a defensible daily routine.",
    proofBuild: "Build",
    proofBuildText:
      "Python collectors, deterministic scoring, source-health checks, tests and GitHub Actions.",
    proofResult: "Result",
    proofResultText:
      "A traceable morning brief, analyst dashboard, API-ready JSON and historical evidence.",
    dailyAutomation: "Daily automation",
    primaryRun: "Primary run",
    recoveryRun: "Recovery run",
    madridTime: "Europe/Madrid",
    generatedOutputs: "Validated outputs",
    outputKinds: "MD · JSON · API · HEALTH · HISTORY",
    openWorkflow: "Inspect GitHub workflow",
    portableEyebrow: "GitHub ↔ Full-stack dashboard",
    sourceBackedFallback: "Source-backed defensive relevance",
    inventoryFallback:
      "Inventory affected products, verify exposure and follow vendor guidance.",
    calculating: "Checking…",
    unavailable: "Not scheduled",
    clearFilters: "Clear filters",
  },
  es: {
    overview: "Hoy",
    vulnerabilities: "Prioridades",
    sources: "Fuentes",
    methodology: "Método",
    engineering: "Proyecto",
    morning: "Resumen diario de amenazas",
    eyebrow: "Inteligencia Blue Team diaria",
    heroA: "Entiende la amenaza.",
    heroB: "Actúa con criterio.",
    heroText:
      "CyberDailyLog reúne fuentes fiables, separa la evidencia del ruido y te muestra qué conviene revisar primero.",
    openBrief: "Ver prioridades",
    how: "Cómo funciona",
    operational: "De la fuente a la acción",
    collect: "Recopilar",
    normalize: "Normalizar",
    score: "Puntuar",
    publish: "Publicar",
    live: "Activo",
    updated: "Actualizado",
    coverage: "Cobertura de 24 horas",
    topPriority: "Prioridad destacada",
    why: "Por qué importa",
    action: "Acción defensiva",
    primarySource: "Abrir fuente primaria",
    noConfirmed: "Sin explotación confirmada",
    notKev: "No consta en CISA KEV",
    assessed: "evaluados",
    above: "sobre el umbral",
    core: "Fuentes principales",
    optional: "Fuentes opcionales",
    healthy: "operativas",
    healthySingle: "operativa",
    riskDistribution: "Distribución del riesgo",
    total: "de elementos de seguridad",
    sourceHealth: "Salud de las fuentes",
    sourceFreshness: "Estado según la última recopilación",
    historical: "Señal de ocho días",
    historicalText:
      "Volumen diario, elementos de alto impacto y estado del proceso desde el archivo.",
    humanContext: "Contexto de analistas",
    community: "Pulso de la comunidad",
    verify: "El interés comunitario es una pista, no inteligencia verificada.",
    readSource: "Leer en la fuente",
    openDiscussion: "Abrir debate",
    allIntel: "Toda la inteligencia priorizada",
    intelIntro:
      "Busca y clasifica el conjunto acotado publicado por la última ejecución.",
    search: "Buscar CVE, producto o descripción",
    allSeverities: "Todas las severidades",
    attentionOnly: "Solo explotación / KEV",
    watchlistOnly: "Solo seguimiento",
    priority: "Prioridad",
    newest: "Más reciente",
    cvss: "CVSS",
    exportJson: "Exportar JSON",
    exportCsv: "Exportar CSV",
    showing: "Mostrando",
    items: "elementos",
    empty: "Ningún elemento coincide con estos filtros.",
    watch: "Añadir a seguimiento",
    unwatch: "Quitar de seguimiento",
    details: "Abrir detalle",
    sourceOperations: "Operación de recopiladores",
    sourceIntro:
      "Inspecciona nivel de confianza, latencia, aceptación y fallos de cada fuente.",
    required: "Principal",
    optionalLabel: "Opcional",
    received: "Recibidos",
    accepted: "Aceptados",
    latency: "Latencia",
    status: "Estado",
    coverageLimits: "Cobertura y límites",
    coverageLimitsText:
      "Comprueba qué respalda esta ejecución, qué fuentes necesitan atención y cómo usamos cada señal.",
    whatWeSee: "Qué podemos ver",
    currentSource: "fuente ha respondido recientemente y sin errores de recopilación.",
    currentSources: "fuentes han respondido recientemente y sin errores de recopilación.",
    intelligenceGaps: "Huecos de inteligencia",
    noGaps: "No se detectan huecos de fuente en esta ejecución.",
    gapSource: "fuente está desactualizada, degradada, caída o solo aporta datos de prueba.",
    gapSources: "fuentes están desactualizadas, degradadas, caídas o solo aportan datos de prueba.",
    coverageCaveat:
      "Un recopilador operativo confirma acceso a esa fuente; no garantiza una visión completa de Internet.",
    fresh: "Reciente",
    late: "Necesita actualizarse",
    unavailableSource: "Sin fecha fiable",
    sourceUse: "Cómo la usamos",
    provenanceGovernment: "Organismo público oficial",
    provenanceAdvisoryRegistry: "Registro coordinado de avisos",
    provenanceProbabilityModel: "Modelo independiente de probabilidad",
    provenanceFirstParty: "Publicación de primera parte",
    provenanceSpecialist: "Editor especializado",
    provenanceCommunity: "Debate comunitario",
    resiliencePath: "Ruta de entrega resiliente",
    resilienceText:
      "El panel cambia de ruta sin ocultar qué fuente está usando en cada momento.",
    used: "En uso",
    available: "Disponible",
    skipped: "En espera",
    unavailableRoute: "No disponible",
    methodTitle: "Transparente por diseño",
    methodIntro:
      "Un proceso reproducible que mantiene las afirmaciones, el contexto y el interés comunitario en niveles de confianza separados.",
    collection: "1. Recopilar",
    collectionText:
      "CISA KEV, NVD, GitHub Advisories y FIRST EPSS aportan evidencia estructurada. RSS y Hacker News añaden contexto etiquetado.",
    normalization: "2. Normalizar",
    normalizationText:
      "Los registros se adaptan a un esquema estable, se deduplican y correlacionan sin ejecutar exploits ni descargar malware.",
    scoring: "3. Puntuar",
    scoringText:
      "Pesos deterministas priorizan explotación, KEV, ransomware, CVSS, EPSS, condiciones de ataque y relevancia defensiva.",
    publication: "4. Publicar",
    publicationText:
      "El informe, la evidencia completa, el canal de datos, la salud de las fuentes y el archivo se validan antes de publicarse.",
    trustBoundaries: "Límites de confianza",
    evidence: "Evidencia",
    evidenceText: "CVE, KEV, EPSS y avisos oficiales.",
    expert: "Contexto experto",
    expertText: "Extractos breves y atribuidos de editores permitidos.",
    communityLane: "Señal comunitaria",
    communityText: "La popularidad nunca se presenta como riesgo verificado.",
    portable: "Un proyecto, dos formas de usarlo",
    portableText:
      "El repositorio funciona por sí solo. Sus datos alimentan esta web y el panel también puede ejecutarse en local o alojarse en otro servicio.",
    repo: "Abrir repositorio",
    runLocal: "Instrucciones autónomas",
    dataContract: "Inspeccionar contrato JSON",
    close: "Cerrar",
    references: "Referencias",
    reasons: "Razones de prioridad",
    actions: "Acciones recomendadas",
    published: "Publicado",
    fetched: "Consulta del panel",
    dataMode: "Fuente de datos",
    liveRepo: "Datos vivos del repositorio",
    snapshot: "Copia verificada de respaldo",
    refreshing: "Actualizando…",
    refresh: "Actualizar datos",
    refreshFailed: "Falló la actualización; se mantiene la copia verificada.",
    refreshed: "Fuentes comprobadas y actualizadas.",
    fallbackRetained:
      "El informe principal no está disponible. Se mantiene un respaldo claramente etiquetado.",
    primaryNavigation: "Navegación principal",
    language: "Idioma",
    runSummary: "Resumen de la ejecución",
    sort: "Ordenar inteligencia",
    critical: "Crítica",
    high: "Alta",
    medium: "Media",
    low: "Baja",
    unknown: "Sin clasificar",
    exploited: "Explotación reportada",
    ransomware: "Vinculada a ransomware",
    yes: "Sí",
    no: "No",
    comments: "comentarios",
    points: "puntos",
    reference: "Referencia",
    totalCollectorTime: "tiempo total de recopilación",
    immediateAttention: "Atención inmediata",
    noImmediate:
      "Ningún elemento de esta ejecución tiene explotación confirmada, consta en CISA KEV o está vinculado a ransomware.",
    immediateCount:
      "elementos requieren revisión inmediata por señales de explotación, KEV o ransomware.",
    scoreLabel: "Puntuación de prioridad · 0–10",
    scoreFormula:
      "CISA KEV +50 · explotación confirmada +40 · ransomware +25 · CVSS crítico +20 · EPSS muy alto +25 · fuente oficial +5",
    statusOperational: "Operativo",
    statusDegraded: "Degradado",
    statusHealthy: "Operativa",
    statusFailed: "Fallida",
    statusFixture: "Datos de prueba",
    statusUnknown: "Desconocido",
    signalDesk: "Radar diario",
    signalDeskTitle: "Más allá de los CVE: qué merece la pena leer hoy",
    signalDeskText:
      "Diarios operativos y pistas de la comunidad recopilados en la misma ejecución, separados claramente por nivel de evidencia.",
    analystBriefs: "Informes de analistas y editores",
    communitySignals: "Señales de la comunidad",
    originalSource: "Contenido original de la fuente",
    originalSourceNote:
      "Los títulos y extractos se mantienen en el idioma original del editor para preservar su precisión.",
    viewSignal: "Abrir señal",
    interviewEyebrow: "Un proyecto demostrable en entrevistas",
    interviewTitle: "No solo sigo las noticias. Construí el sistema.",
    interviewQuote:
      "CyberDailyLog demuestra cómo trabajo: un sistema Blue Team reproducible que recopila, valida, prioriza y publica un informe diario.",
    proofProblem: "Problema",
    proofProblemText:
      "La información de seguridad está fragmentada, genera ruido y cuesta convertirla en una rutina diaria defendible.",
    proofBuild: "Construcción",
    proofBuildText:
      "Recopiladores en Python, priorización determinista, controles de salud, pruebas y GitHub Actions.",
    proofResult: "Resultado",
    proofResultText:
      "Informe diario trazable, panel de análisis, JSON integrable e histórico verificable.",
    dailyAutomation: "Automatización diaria",
    primaryRun: "Ejecución principal",
    recoveryRun: "Ejecución de recuperación",
    madridTime: "Europa/Madrid",
    generatedOutputs: "Salidas validadas",
    outputKinds: "MD · JSON · API · SALUD · HISTÓRICO",
    openWorkflow: "Ver automatización en GitHub",
    portableEyebrow: "GitHub ↔ Panel web",
    sourceBackedFallback: "Relevancia defensiva respaldada por la fuente",
    inventoryFallback:
      "Inventaría los productos afectados, verifica la exposición y sigue las indicaciones del proveedor.",
    calculating: "Comprobando…",
    unavailable: "Sin programar",
    clearFilters: "Limpiar filtros",
  },
} as const;

const SEVERITY_ORDER: Severity[] = [
  "CRITICAL",
  "HIGH",
  "MEDIUM",
  "LOW",
  "UNKNOWN",
];

const VIEW_KEYS: View[] = [
  "overview",
  "vulnerabilities",
  "sources",
  "methodology",
  "engineering",
];

function readLocalPreference(key: string) {
  try {
    return window.localStorage.getItem(key);
  } catch {
    return null;
  }
}

function writeLocalPreference(key: string, value: string) {
  try {
    window.localStorage.setItem(key, value);
  } catch {
    // The interface still works when private browsing blocks local storage.
  }
}

function removeLocalPreference(key: string) {
  try {
    window.localStorage.removeItem(key);
  } catch {
    // Nothing to remove when browser storage is unavailable.
  }
}
const MIN_VALID_TIMESTAMP = Date.UTC(2000, 0, 1);
const MONTHS = {
  en: {
    short: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    long: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
  },
  es: {
    short: ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sept", "oct", "nov", "dic"],
    long: ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
  },
} as const;

function parseTimestamp(value: string) {
  const timestamp = Date.parse(value);
  return Number.isFinite(timestamp) && timestamp >= MIN_VALID_TIMESTAMP
    ? timestamp
    : null;
}

function formatDate(value: string, language: Language, short = false) {
  const timestamp = parseTimestamp(value);
  if (timestamp === null) return "—";
  const date = new Date(timestamp);
  const day = String(date.getUTCDate()).padStart(2, "0");
  const month = MONTHS[language][short ? "short" : "long"][date.getUTCMonth()];
  const year = date.getUTCFullYear();
  if (short) return `${day} ${month} ${year}`;
  const time = `${String(date.getUTCHours()).padStart(2, "0")}:${String(date.getUTCMinutes()).padStart(2, "0")}`;
  return language === "es"
    ? `${day} de ${month} de ${year} · ${time}`
    : `${day} ${month} ${year} · ${time}`;
}

function formatRelative(value: string, language: Language, now: number | null) {
  const timestamp = parseTimestamp(value);
  if (timestamp === null || now === null) return COPY[language].calculating;
  const milliseconds = now - timestamp;
  const minutes = Math.max(0, Math.round(milliseconds / 60_000));
  if (minutes < 60) return language === "es" ? `hace ${minutes} min` : `${minutes}m ago`;
  const hours = Math.round(minutes / 60);
  if (hours < 48) return language === "es" ? `hace ${hours} h` : `${hours}h ago`;
  const days = Math.round(hours / 24);
  return language === "es" ? `hace ${days} d` : `${days}d ago`;
}

function formatCountdown(value: string, now: number | null, language: Language) {
  const target = parseTimestamp(value);
  if (target === null || now === null) return COPY[language].calculating;
  const remaining = Math.max(0, target - now);
  if (remaining <= 0) {
    return language === "es" ? "ahora" : "now";
  }
  const totalSeconds = Math.ceil(remaining / 1_000);
  const hours = Math.floor(totalSeconds / 3_600);
  const minutes = Math.floor((totalSeconds % 3_600) / 60);
  const seconds = totalSeconds % 60;
  return [hours, minutes, seconds]
    .map((part) => String(part).padStart(2, "0"))
    .join(":");
}

function nextMadridRunLabel(now: number | null, language: Language) {
  if (now === null) return COPY[language].calculating;
  const parts = new Intl.DateTimeFormat("en-GB", {
    timeZone: "Europe/Madrid",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
  }).formatToParts(new Date(now));
  const value = (type: Intl.DateTimeFormatPartTypes) =>
    Number(parts.find((part) => part.type === type)?.value ?? 0);
  const currentMinutes = value("hour") * 60 + value("minute");
  const primaryMinutes = 8 * 60 + 17;
  const recoveryMinutes = 9 * 60 + 47;
  const useRecovery =
    currentMinutes >= primaryMinutes && currentMinutes < recoveryMinutes;
  const useNextDay = currentMinutes >= recoveryMinutes;
  const nextHour = useRecovery ? 9 : 8;
  const nextMinute = useRecovery ? 47 : 17;
  const wallDate = new Date(
    Date.UTC(
      value("year"),
      value("month") - 1,
      value("day") + Number(useNextDay),
      nextHour,
      nextMinute,
    ),
  );
  const date = new Intl.DateTimeFormat(language === "es" ? "es-ES" : "en-GB", {
    day: "2-digit",
    month: "short",
    timeZone: "UTC",
  }).format(wallDate);
  return `${date} · ${String(nextHour).padStart(2, "0")}:${String(nextMinute).padStart(2, "0")}`;
}

function isStaleSnapshot(value: string, now: number | null) {
  const generatedAt = parseTimestamp(value);
  return generatedAt === null || (now !== null && now - generatedAt > 36 * 3_600_000);
}

function percent(value: number | null) {
  if (value === null) return "—";
  return `${(value * 100).toFixed(value < 0.01 ? 2 : 1)}%`;
}

function compactNumber(value: number, language: Language = "en") {
  if (value < 1_000) return String(value);

  const divisor = value >= 1_000_000 ? 1_000_000 : 1_000;
  const suffix = value >= 1_000_000 ? "M" : language === "es" ? " mil" : "k";
  const scaled = Math.round((value / divisor) * 10) / 10;
  const formatted = Number.isInteger(scaled)
    ? String(scaled)
    : String(scaled).replace(".", language === "es" ? "," : ".");

  return `${formatted}${suffix}`;
}

function severityLabel(severity: Severity, language: Language) {
  const t = COPY[language];
  return {
    CRITICAL: t.critical,
    HIGH: t.high,
    MEDIUM: t.medium,
    LOW: t.low,
    UNKNOWN: t.unknown,
  }[severity];
}

function statusLabel(status: SourceHealth["status"], language: Language) {
  const t = COPY[language];
  return {
    healthy: t.statusHealthy,
    degraded: t.statusDegraded,
    failed: t.statusFailed,
    fixture_only: t.statusFixture,
    unknown: t.statusUnknown,
  }[status];
}

function trustLaneLabel(lane: SourceTrustLane, language: Language) {
  const t = COPY[language];
  return {
    evidence: t.evidence,
    expert: t.expert,
    community: t.communityLane,
  }[lane];
}

function provenanceLabel(provenance: SourceProvenance, language: Language) {
  const t = COPY[language];
  return {
    government: t.provenanceGovernment,
    advisory_registry: t.provenanceAdvisoryRegistry,
    probability_model: t.provenanceProbabilityModel,
    first_party: t.provenanceFirstParty,
    specialist: t.provenanceSpecialist,
    community: t.provenanceCommunity,
  }[provenance];
}

function hasRecentHealthyRun(source: SourceHealth, now: number | null) {
  const finishedAt = parseTimestamp(source.finishedAt);
  if (source.status !== "healthy" || finishedAt === null) return false;
  return now === null || now - finishedAt <= 36 * 3_600_000;
}

function sourceFreshnessLabel(
  source: SourceHealth,
  language: Language,
  now: number | null,
) {
  if (parseTimestamp(source.finishedAt) === null) {
    return COPY[language].unavailableSource;
  }
  return hasRecentHealthyRun(source, now)
    ? COPY[language].fresh
    : COPY[language].late;
}

function deliveryStatusLabel(
  status: DashboardData["deliveryChain"][number]["status"],
  language: Language,
) {
  const t = COPY[language];
  return {
    used: t.used,
    available: t.available,
    skipped: t.skipped,
    failed: t.unavailableRoute,
  }[status];
}

function deliveryLabel(
  id: DashboardData["deliveryChain"][number]["id"],
  language: Language,
) {
  const labels = {
    en: {
      "github-raw": "Repository report",
      "jsdelivr-cdn": "Repository CDN mirror",
      "official-apis": "NVD + CISA KEV + FIRST EPSS",
      "bundled-snapshot": "Verified bundled snapshot",
    },
    es: {
      "github-raw": "Informe del repositorio",
      "jsdelivr-cdn": "Espejo CDN del repositorio",
      "official-apis": "NVD + CISA KEV + FIRST EPSS",
      "bundled-snapshot": "Copia verificada incluida",
    },
  } as const;
  return labels[language][id];
}

function pipelineLabel(
  status: DashboardData["pipelineStatus"],
  language: Language,
) {
  return status === "operational"
    ? COPY[language].statusOperational
    : COPY[language].statusDegraded;
}

function localizedReason(value: string, language: Language) {
  if (language === "en") return value;
  return value
    .replace(/official source/gi, "fuente oficial")
    .replace(/detection opportunity/gi, "oportunidad de detección")
    .replace(/confirmed exploitation/gi, "explotación confirmada")
    .replace(/priority technology/gi, "tecnología prioritaria")
    .replace(/critical CVSS/gi, "CVSS crítico")
    .replace(/source-backed defensive relevance/gi, "relevancia defensiva respaldada por la fuente");
}

function localizedAction(value: string, language: Language) {
  if (language === "en") return value;
  if (
    /inventory affected products.*verify exposure.*vendor/i.test(value)
  ) {
    return COPY.es.inventoryFallback;
  }
  return value;
}

function severityClass(severity: Severity) {
  return `severity-${severity.toLowerCase()}`;
}

function attentionItem(item: Vulnerability) {
  return item.cisaKev || item.knownExploited || item.knownRansomwareUse;
}

function Icon({
  name,
  size = 20,
}: {
  name:
    | "arrow"
    | "calendar"
    | "check"
    | "database"
    | "download"
    | "external"
    | "filter"
    | "github"
    | "pulse"
    | "refresh"
    | "search"
    | "shield"
    | "star"
    | "x";
  size?: number;
}) {
  const paths = {
    arrow: <path d="M5 12h14m-5-5 5 5-5 5" />,
    calendar: (
      <>
        <rect x="3" y="5" width="18" height="16" rx="2" />
        <path d="M16 3v4M8 3v4M3 10h18" />
      </>
    ),
    check: <path d="m5 12 4 4L19 6" />,
    database: (
      <>
        <ellipse cx="12" cy="5" rx="8" ry="3" />
        <path d="M4 5v7c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 12v7c0 1.7 3.6 3 8 3s8-1.3 8-3v-7" />
      </>
    ),
    download: (
      <>
        <path d="M12 3v12m-5-5 5 5 5-5" />
        <path d="M5 21h14" />
      </>
    ),
    external: <path d="M14 4h6v6m0-6L10 14M8 6H4v14h14v-4" />,
    filter: <path d="M4 6h16M7 12h10m-7 6h4" />,
    github: (
      <path d="M12 2a10 10 0 0 0-3.16 19.49c.5.09.68-.22.68-.48v-1.69c-2.78.6-3.37-1.18-3.37-1.18-.46-1.15-1.11-1.46-1.11-1.46-.91-.62.07-.61.07-.61 1 .07 1.53 1.03 1.53 1.03.9 1.53 2.35 1.09 2.92.83.09-.65.35-1.09.64-1.34-2.22-.25-4.56-1.11-4.56-4.94 0-1.09.39-1.98 1.03-2.68-.1-.25-.45-1.27.1-2.64 0 0 .84-.27 2.75 1.02A9.6 9.6 0 0 1 12 7.01c.85 0 1.71.11 2.51.34 1.91-1.29 2.75-1.02 2.75-1.02.55 1.37.2 2.39.1 2.64.64.7 1.03 1.59 1.03 2.68 0 3.84-2.34 4.68-4.57 4.93.36.31.68.92.68 1.85v2.75c0 .27.18.58.69.48A10 10 0 0 0 12 2Z" />
    ),
    pulse: <path d="M3 12h4l2-7 4 14 2-7h6" />,
    refresh: (
      <>
        <path d="M20 7v5h-5" />
        <path d="M19 12a7 7 0 1 0-2 5" />
      </>
    ),
    search: (
      <>
        <circle cx="11" cy="11" r="7" />
        <path d="m20 20-4-4" />
      </>
    ),
    shield: <path d="M12 3 4 6v6c0 5 3.4 8.3 8 10 4.6-1.7 8-5 8-10V6l-8-3Zm-3 9 2 2 4-5" />,
    star: <path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-2.9-5.6 2.9 1.1-6.2L3 9.6l6.2-.9L12 3Z" />,
    x: <path d="m6 6 12 12M18 6 6 18" />,
  };
  return (
    <svg
      aria-hidden="true"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill={name === "github" ? "currentColor" : "none"}
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {paths[name]}
    </svg>
  );
}

function Pipeline({
  language,
  status,
  dataMode,
}: {
  language: Language;
  status: DashboardData["pipelineStatus"];
  dataMode: DashboardData["dataMode"];
}) {
  const t = COPY[language];
  const state =
    dataMode === "repository-snapshot"
      ? language === "es"
        ? "Respaldo"
        : "Fallback"
      : dataMode === "official-backup"
        ? language === "es"
          ? "API oficial"
          : "Official API"
      : status === "degraded"
        ? language === "es"
          ? "Degradado"
          : "Degraded"
        : t.live;
  const steps = [
    [t.collect, "↓"],
    [t.normalize, "≡"],
    [t.score, "◇"],
    [t.publish, "↗"],
  ];
  return (
    <div className="pipeline" aria-label={t.operational}>
      <div className="section-label">{t.operational}</div>
      <div className="pipeline-steps">
        {steps.map(([label, glyph], index) => (
          <div className="pipeline-step" key={label}>
            <span className="pipeline-icon">{glyph}</span>
            <strong>{label}</strong>
            <small className={dataMode === "live" ? status : dataMode}>
              {state}
            </small>
            {index < steps.length - 1 ? (
              <span className="pipeline-arrow" aria-hidden="true">
                →
              </span>
            ) : null}
          </div>
        ))}
      </div>
    </div>
  );
}

function DataDelivery({
  data,
  language,
  now,
}: {
  data: DashboardData;
  language: Language;
  now: number | null;
}) {
  const stale = isStaleSnapshot(data.generatedAt, now);
  const copy =
    language === "es"
      ? {
          label: "Estado de los datos",
          published: "Informe generado",
          recheck: "Nueva comprobación",
          daily: "Publicación prevista",
          live: "Conectado al repositorio",
          official: "Respaldo oficial activo",
          fallback: "Informe de respaldo verificado",
          stale: "El informe necesita actualizarse",
          note: "El panel comprueba la mejor ruta disponible automáticamente. También puedes actualizarlo desde la cabecera.",
        }
      : {
          label: "Data status",
          published: "Report generated",
          recheck: "Next check",
          daily: "Expected publication",
          live: "Connected to the repository",
          official: "Official backup active",
          fallback: "Verified backup report",
          stale: "The report needs an update",
          note: "The dashboard checks the best available route automatically. You can also refresh it from the header.",
        };

  return (
    <section className={`delivery-card ${stale ? "stale" : ""}`}>
      <div className="delivery-heading">
        <span className="section-label">{copy.label}</span>
        <span className={`delivery-mode ${data.dataMode}`}>
          <i />
          {data.dataMode === "live" && !stale
            ? copy.live
            : data.dataMode === "official-backup"
              ? copy.official
            : data.dataMode === "repository-snapshot"
              ? copy.fallback
              : copy.stale}
        </span>
      </div>
      <div className="delivery-grid">
        <div>
          <span>{copy.published}</span>
          <strong>{formatDate(data.generatedAt, language, true)}</strong>
          <small>{formatRelative(data.generatedAt, language, now)}</small>
        </div>
        <div>
          <span>{copy.recheck}</span>
          <strong>{formatCountdown(data.nextRefreshAt, now, language)}</strong>
          <small>{language === "es" ? `cada ${data.refreshIntervalMinutes} min` : `every ${data.refreshIntervalMinutes} min`}</small>
        </div>
        <div>
          <span>{copy.daily}</span>
          <strong>{nextMadridRunLabel(now, language)}</strong>
          <small>{language === "es" ? "hora de Madrid" : "Madrid time"}</small>
        </div>
      </div>
      <p>{copy.note}</p>
    </section>
  );
}

function FreshnessBanner({
  data,
  language,
  now,
  refreshing,
  onRefresh,
}: {
  data: DashboardData;
  language: Language;
  now: number | null;
  refreshing: boolean;
  onRefresh: () => void;
}) {
  const stale = isStaleSnapshot(data.generatedAt, now);
  if (data.dataMode === "live" && !stale) return null;
  const copy =
    language === "es"
      ? data.dataMode === "official-backup"
        ? {
            title: "Respaldo oficial en uso",
            text: "El informe del repositorio no estaba disponible o actualizado. Mostramos NVD y CISA KEV, con EPSS cuando responde; el contexto editorial queda fuera.",
            action: "Comprobar ruta principal",
          }
        : data.dataMode === "repository-snapshot"
          ? {
              title: "Mostrando el último informe verificado",
              text: `No respondió ninguna fuente en vivo. Conservamos el informe del ${formatDate(data.generatedAt, language, true)} para no dejarte sin contexto.`,
              action: "Comprobar ahora",
            }
          : {
              title: "El informe necesita actualizarse",
              text: `La última publicación fue el ${formatDate(data.generatedAt, language, true)}. Los datos siguen visibles, pero deben tratarse como antiguos.`,
              action: "Actualizar",
            }
      : data.dataMode === "official-backup"
        ? {
            title: "Official backup in use",
            text: "The repository report was unavailable or out of date. NVD and CISA KEV are shown, with EPSS when available; editorial context is omitted.",
            action: "Check primary route",
          }
        : data.dataMode === "repository-snapshot"
          ? {
              title: "Showing the last verified report",
              text: `No live source responded. The ${formatDate(data.generatedAt, language, true)} report remains visible so the page still has context.`,
              action: "Check now",
            }
          : {
              title: "The report needs an update",
              text: `The last publication was ${formatDate(data.generatedAt, language, true)}. It remains visible but should be treated as old.`,
              action: "Refresh",
            };
  return (
    <aside className={`freshness-banner ${data.dataMode}`} role="status">
      <span className="freshness-icon" aria-hidden="true">!</span>
      <div>
        <strong>{copy.title}</strong>
        <p>{copy.text}</p>
      </div>
      <button onClick={onRefresh} disabled={refreshing}>
        <span className={refreshing ? "spinning" : ""}><Icon name="refresh" size={17} /></span>
        {refreshing ? COPY[language].refreshing : copy.action}
      </button>
    </aside>
  );
}

function RiskDistribution({
  data,
  language,
}: {
  data: DashboardData;
  language: Language;
}) {
  const t = COPY[language];
  const maximum = Math.max(...data.distribution.map((item) => item.count), 1);
  const total = data.distribution.reduce((sum, item) => sum + item.count, 0);
  return (
    <section className="paper-panel risk-panel" aria-labelledby="risk-title">
      <div className="panel-heading">
        <div>
          <span className="section-label" id="risk-title">
            {t.riskDistribution}
          </span>
          <span className="heading-stat">
            <strong>{data.assessed}</strong> {t.assessed}
          </span>
        </div>
        <span className="threshold-stat">
          <strong>{data.aboveThreshold}</strong> {t.above}
        </span>
      </div>
      <div className="risk-bars">
        {data.distribution.map((item) => (
          <div className="risk-row" key={item.key}>
            <span className="risk-label">
              <i style={{ background: item.color }} />
              {severityLabel(item.key, language)}
            </span>
            <span className="risk-track">
              <span
                className="risk-fill"
                style={{
                  width: `${Math.max(2, (item.count / maximum) * 100)}%`,
                  background: item.color,
                }}
              />
            </span>
            <strong>{item.count}</strong>
            <span className="risk-percent">
              {total ? `${((item.count / total) * 100).toFixed(1)}%` : "—"}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}

function PriorityCard({
  item,
  language,
  onOpen,
}: {
  item: Vulnerability;
  language: Language;
  onOpen: () => void;
}) {
  const t = COPY[language];
  return (
    <article className="priority-card">
      <div className="priority-ribbon">
        <span aria-hidden="true">△</span>
        {t.topPriority}
      </div>
      <button className="priority-title-button" onClick={onOpen}>
        <span>{item.id}</span>
      </button>
      <div className="priority-score-row">
        <strong>{item.priorityScore.toFixed(1)}</strong>
        <div>
          <span>{severityLabel(item.severity, language)}</span>
          <h2>{item.title}</h2>
        </div>
      </div>
      <div className="priority-facts">
        <span>
          <i>◈</i>
          {item.cvssScore === null ? "CVSS —" : `CVSS ${item.cvssScore.toFixed(1)}`}
        </span>
        <span>
          <i>⌁</i>
          {item.cisaKev ? "CISA KEV" : t.notKev}
        </span>
        <span>
          <i>◎</i>
          {item.knownExploited ? t.exploited : t.noConfirmed}
        </span>
        <span>
          <i>□</i>
          {formatDate(item.publishedAt, language, true)}
        </span>
      </div>
      <p className="priority-summary">{item.summary}</p>
      <div className="priority-footer">
        <button className="text-action" onClick={onOpen}>
          {t.details} <Icon name="arrow" size={17} />
        </button>
        <a href={item.sourceUrl} target="_blank" rel="noreferrer">
          {t.primarySource} <Icon name="external" size={16} />
        </a>
      </div>
    </article>
  );
}

function MetricStrip({
  data,
  language,
}: {
  data: DashboardData;
  language: Language;
}) {
  const t = COPY[language];
  const core = data.sourceHealth.filter((source) => source.required);
  const optional = data.sourceHealth.filter((source) => !source.required);
  const coreHealthy = core.filter((source) =>
    ["healthy", "fixture_only"].includes(source.status),
  ).length;
  const optionalHealthy = optional.filter((source) =>
    ["healthy", "fixture_only"].includes(source.status),
  ).length;
  return (
    <section className="metric-strip" aria-label={t.runSummary}>
      <div className="metric">
        <span className="metric-icon blue">
          <Icon name="database" />
        </span>
        <strong>{data.assessed}</strong>
        <span>{t.assessed}</span>
      </div>
      <div className="metric">
        <span className="metric-icon orange">
          <Icon name="pulse" />
        </span>
        <strong>{data.aboveThreshold}</strong>
        <span>{t.above}</span>
      </div>
      <div className="metric">
        <span className="metric-icon green">
          <Icon name="shield" />
        </span>
        <strong>
          {coreHealthy}/{core.length}
        </strong>
        <span>{t.core}</span>
      </div>
      <div className="metric">
        <span className="metric-icon green">
          <Icon name="pulse" />
        </span>
        <strong>{optionalHealthy}</strong>
        <span>{t.optional} · {t.healthy}</span>
      </div>
    </section>
  );
}

function SourceRail({
  sources,
  language,
  now,
}: {
  sources: SourceHealth[];
  language: Language;
  now: number | null;
}) {
  const t = COPY[language];
  return (
    <section className="paper-panel source-rail" aria-labelledby="source-rail-title">
      <div className="panel-heading">
        <span className="section-label" id="source-rail-title">
          {t.sourceHealth}
        </span>
        <span className="panel-note">{t.sourceFreshness}</span>
      </div>
      <div className="source-rail-grid">
        {sources.map((source) => (
          <a
            className="source-rail-item"
            href={SOURCE_URLS[source.source] ?? "#"}
            key={source.source}
            target="_blank"
            rel="noreferrer"
          >
            <span className="source-monogram">
              {SOURCE_SHORT_LABELS[source.source]?.slice(0, 2) ??
                source.label.slice(0, 2)}
            </span>
            <span>
              <strong>
                {SOURCE_SHORT_LABELS[source.source] ?? source.label}
              </strong>
              <small>
                <i className={`health-dot ${source.status}`} />
                {source.status === "healthy"
                  ? formatRelative(source.finishedAt, language, now)
                  : statusLabel(source.status, language)}
              </small>
            </span>
          </a>
        ))}
      </div>
    </section>
  );
}

function HistoryChart({
  history,
  language,
}: {
  history: HistoryPoint[];
  language: Language;
}) {
  const t = COPY[language];
  if (history.length < 2) {
    const point = history[0];
    const copy =
      language === "es"
        ? {
            title: "Histórico sin fabricar",
            text: "El repositorio conserva el histórico diario, pero todavía no publica una serie de datos acotada para esta gráfica. Mostramos solo el punto actual en vez de inventar una tendencia.",
            open: "Abrir archivo diario",
          }
        : {
            title: "History without guesswork",
            text: "The repository preserves its daily archive, but it does not yet publish a bounded feed for this chart. Only the current point is shown instead of inventing a trend.",
            open: "Open daily archive",
          };
    return (
      <section className="paper-panel history-panel history-empty">
        <div>
          <span className="section-label">{copy.title}</span>
          <p>{copy.text}</p>
        </div>
        {point ? (
          <div className="history-current-point">
            <span>{point.date}</span>
            <strong>{point.assessed}</strong>
            <small>{t.assessed}</small>
            <b>{point.aboveThreshold} {t.above}</b>
          </div>
        ) : null}
        <a
          href="https://github.com/JimBLogic/CyberDailyLog/tree/main/reports/archive"
          target="_blank"
          rel="noreferrer"
        >
          {copy.open} <Icon name="external" size={15} />
        </a>
      </section>
    );
  }
  const width = 760;
  const height = 260;
  const padX = 40;
  const padY = 30;
  const maximum = Math.max(...history.map((point) => point.assessed), 1);
  const x = (index: number) =>
    padX + (index / Math.max(history.length - 1, 1)) * (width - padX * 2);
  const y = (value: number) =>
    height - padY - (value / maximum) * (height - padY * 2);
  const assessedPath = history
    .map((point, index) => `${index ? "L" : "M"} ${x(index)} ${y(point.assessed)}`)
    .join(" ");
  const abovePath = history
    .map(
      (point, index) =>
        `${index ? "L" : "M"} ${x(index)} ${y(point.aboveThreshold)}`,
    )
    .join(" ");
  return (
    <section className="paper-panel history-panel">
      <div className="panel-heading">
        <div>
          <span className="section-label">{t.historical}</span>
          <p>{t.historicalText}</p>
        </div>
        <div className="chart-legend">
          <span><i className="legend-blue" />{t.assessed}</span>
          <span><i className="legend-red" />{t.above}</span>
        </div>
      </div>
      <svg
        className="history-chart"
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-label={`${t.historical}: ${history.length} ${t.points}`}
      >
        {[0, 0.25, 0.5, 0.75, 1].map((ratio) => (
          <g key={ratio}>
            <line
              x1={padX}
              y1={y(maximum * ratio)}
              x2={width - padX}
              y2={y(maximum * ratio)}
              className="chart-grid-line"
            />
            <text x={4} y={y(maximum * ratio) + 4} className="chart-label">
              {compactNumber(Math.round(maximum * ratio), language)}
            </text>
          </g>
        ))}
        <path d={assessedPath} className="chart-line assessed-line" />
        <path d={abovePath} className="chart-line above-line" />
        {history.map((point, index) => (
          <g key={point.date}>
            <circle
              cx={x(index)}
              cy={y(point.assessed)}
              r="4"
              className="chart-dot assessed-dot"
            >
              <title>{`${point.date}: ${point.assessed} ${t.assessed}`}</title>
            </circle>
            <circle
              cx={x(index)}
              cy={y(point.aboveThreshold)}
              r="4"
              className="chart-dot above-dot"
            >
              <title>{`${point.date}: ${point.aboveThreshold} ${t.above}`}</title>
            </circle>
            <text
              x={x(index)}
              y={height - 6}
              textAnchor="middle"
              className="chart-label chart-date"
            >
              {point.date.slice(5).replace("-", "/")}
            </text>
          </g>
        ))}
      </svg>
    </section>
  );
}

function SourceArtwork({
  url,
  source,
}: {
  url: string;
  source: string;
}) {
  const [failed, setFailed] = useState(false);
  if (!url || failed) {
    return (
      <div className="source-artwork source-artwork-fallback" aria-hidden="true">
        <span>{source.slice(0, 1)}</span>
        <i />
      </div>
    );
  }
  return (
    <div className="source-artwork">
      {/* The backend only permits and proxies images discovered on allowlisted sources. */}
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={`/api/source-media?url=${encodeURIComponent(url)}`}
        alt=""
        onError={() => setFailed(true)}
      />
    </div>
  );
}

function SignalDesk({
  data,
  language,
}: {
  data: DashboardData;
  language: Language;
}) {
  const t = COPY[language];
  const analysts =
    data.analystBriefs.length > 0
      ? data.analystBriefs
      : data.humanContext
        ? [data.humanContext]
        : [];
  const community =
    data.communitySignals.length > 0
      ? data.communitySignals
      : data.communityPulse
        ? [data.communityPulse]
        : [];
  return (
    <section className="signal-desk" aria-labelledby="signal-desk-title">
      <div className="signal-desk-heading">
        <div>
          <span className="eyebrow">{t.signalDesk}</span>
          <h2 id="signal-desk-title">{t.signalDeskTitle}</h2>
          <p>{t.signalDeskText}</p>
        </div>
        <div className="original-language-note">
          <strong>{t.originalSource}</strong>
          <span>{t.originalSourceNote}</span>
        </div>
      </div>
      <div className="signal-columns">
        <div className="signal-column">
          <div className="signal-column-title">
            <span>{t.analystBriefs}</span>
            <strong>{analysts.length}</strong>
          </div>
          <div className="signal-list">
            {analysts.map((item, index) => (
              <article
                className={`signal-card analyst-signal ${index === 0 ? "featured" : ""}`}
                key={`${item.sourceUrl}-${item.publishedAt}`}
              >
                <SourceArtwork url={item.sourceUrl} source={item.sourceName} />
                <div className="signal-card-copy">
                  <span className="context-kicker">{t.humanContext}</span>
                  <h3>{item.title}</h3>
                  <p>{item.excerpt}</p>
                  <div className="signal-meta">
                    <span>
                      {item.sourceName} ·{" "}
                      {formatDate(item.publishedAt, language, true)}
                    </span>
                    <a href={item.sourceUrl} target="_blank" rel="noreferrer">
                      {t.readSource} <Icon name="external" size={14} />
                    </a>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </div>
        <div className="signal-column community-column">
          <div className="signal-column-title">
            <span>{t.communitySignals}</span>
            <strong>{community.length}</strong>
          </div>
          <div className="signal-list">
            {community.map((item, index) => (
              <article
                className={`signal-card community-signal ${index === 0 ? "featured" : ""}`}
                key={`${item.discussionUrl}-${item.publishedAt}`}
              >
                <SourceArtwork url={item.sourceUrl} source={item.sourceName} />
                <div className="signal-card-copy">
                  <span className="context-kicker">{t.community}</span>
                  <h3>{item.title}</h3>
                  <p>{t.verify}</p>
                  <div className="community-metrics">
                    <span>
                      <strong>{item.score}</strong> {t.points}
                    </span>
                    <span>
                      <strong>{item.comments}</strong> {t.comments}
                    </span>
                  </div>
                  <div className="signal-meta">
                    <span>{item.sourceName}</span>
                    <a
                      href={item.discussionUrl}
                      target="_blank"
                      rel="noreferrer"
                    >
                      {t.openDiscussion} <Icon name="external" size={14} />
                    </a>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function InterviewProof({
  data,
  language,
}: {
  data: DashboardData;
  language: Language;
}) {
  const t = COPY[language];
  const cards = [
    [t.proofProblem, t.proofProblemText, "01"],
    [t.proofBuild, t.proofBuildText, "02"],
    [t.proofResult, t.proofResultText, "03"],
  ];
  return (
    <section className="interview-proof">
      <div className="proof-story">
        <span className="eyebrow">{t.interviewEyebrow}</span>
        <h2>{t.interviewTitle}</h2>
        <blockquote>{t.interviewQuote}</blockquote>
        <div className="proof-cards">
          {cards.map(([title, text, number]) => (
            <article key={title}>
              <span>{number}</span>
              <strong>{title}</strong>
              <p>{text}</p>
            </article>
          ))}
        </div>
      </div>
      <aside className="automation-card">
        <span className="section-label">{t.dailyAutomation}</span>
        <div>
          <span>{t.primaryRun}</span>
          <strong>08:17</strong>
          <small>{t.madridTime}</small>
        </div>
        <div>
          <span>{t.recoveryRun}</span>
          <strong>09:47</strong>
          <small>{t.madridTime}</small>
        </div>
        <div>
          <span>{t.generatedOutputs}</span>
          <strong>5</strong>
          <small>{t.outputKinds}</small>
        </div>
        <a
          href={`${data.repositoryUrl}/actions/workflows/daily-intelligence.yml`}
          target="_blank"
          rel="noreferrer"
        >
          {t.openWorkflow} <Icon name="external" size={15} />
        </a>
      </aside>
    </section>
  );
}

function VulnerabilityList({
  data,
  language,
  watchlist,
  onWatchlist,
  onOpen,
}: {
  data: DashboardData;
  language: Language;
  watchlist: Set<string>;
  onWatchlist: (id: string) => void;
  onOpen: (item: Vulnerability) => void;
}) {
  const t = COPY[language];
  const [query, setQuery] = useState("");
  const [severity, setSeverity] = useState<Severity | "ALL">("ALL");
  const [attention, setAttention] = useState(false);
  const [watchOnly, setWatchOnly] = useState(false);
  const [sort, setSort] = useState<"priority" | "newest" | "cvss">("priority");
  const items = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return data.vulnerabilities
      .filter((item) => severity === "ALL" || item.severity === severity)
      .filter((item) => !attention || attentionItem(item))
      .filter((item) => !watchOnly || watchlist.has(item.id))
      .filter(
        (item) =>
          !needle ||
          [item.id, item.title, item.summary, ...item.products]
            .join(" ")
            .toLowerCase()
            .includes(needle),
      )
      .sort((a, b) => {
        if (sort === "newest") {
          return Date.parse(b.publishedAt) - Date.parse(a.publishedAt);
        }
        if (sort === "cvss") {
          return (b.cvssScore ?? -1) - (a.cvssScore ?? -1);
        }
        return b.priorityScore - a.priorityScore;
      });
  }, [attention, data.vulnerabilities, query, severity, sort, watchOnly, watchlist]);

  return (
    <section className="view-section">
      <div className="view-heading">
        <div>
          <span className="eyebrow">{t.eyebrow}</span>
          <h1>{t.allIntel}</h1>
          <p>{t.intelIntro}</p>
        </div>
        <div className="export-actions">
          <a className="button secondary compact" href="/api/export?format=json">
            <Icon name="download" size={17} /> {t.exportJson}
          </a>
          <a className="button secondary compact" href="/api/export?format=csv">
            <Icon name="download" size={17} /> {t.exportCsv}
          </a>
        </div>
      </div>
      <div className="filter-bar">
        <label className="search-field">
          <Icon name="search" size={18} />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder={t.search}
          />
        </label>
        <label className="select-field">
          <span className="sr-only">{t.allSeverities}</span>
          <select
            value={severity}
            onChange={(event) =>
              setSeverity(event.target.value as Severity | "ALL")
            }
          >
            <option value="ALL">{t.allSeverities}</option>
            {SEVERITY_ORDER.map((value) => (
              <option value={value} key={value}>
                {severityLabel(value, language)}
              </option>
            ))}
          </select>
        </label>
        <button
          className={`filter-toggle ${attention ? "active" : ""}`}
          onClick={() => setAttention((value) => !value)}
          aria-pressed={attention}
        >
          <Icon name="filter" size={17} /> {t.attentionOnly}
        </button>
        <button
          className={`filter-toggle ${watchOnly ? "active" : ""}`}
          onClick={() => setWatchOnly((value) => !value)}
          aria-pressed={watchOnly}
        >
          <Icon name="star" size={17} /> {t.watchlistOnly}
        </button>
        <div className="sort-group" aria-label={t.sort}>
          {(["priority", "newest", "cvss"] as const).map((value) => (
            <button
              className={sort === value ? "active" : ""}
              onClick={() => setSort(value)}
              key={value}
            >
              {t[value]}
            </button>
          ))}
        </div>
      </div>
      <div className="list-summary">
        {t.showing} <strong>{items.length}</strong> {t.items}
      </div>
      <div className="vulnerability-list">
        {items.map((item) => (
          <article className="vulnerability-row" key={item.id}>
            <button
              className={`watch-button ${watchlist.has(item.id) ? "active" : ""}`}
              onClick={() => onWatchlist(item.id)}
              aria-label={watchlist.has(item.id) ? t.unwatch : t.watch}
              title={watchlist.has(item.id) ? t.unwatch : t.watch}
            >
              <Icon name="star" size={18} />
            </button>
            <div className={`severity-marker ${severityClass(item.severity)}`}>
              <span>{item.priorityScore.toFixed(1)}</span>
              <small>{severityLabel(item.severity, language)}</small>
            </div>
            <button className="vulnerability-main" onClick={() => onOpen(item)}>
              <span className="vulnerability-id">{item.id}</span>
              <strong>{item.title}</strong>
              <span className="vulnerability-summary">{item.summary}</span>
              <span className="vulnerability-meta">
                {item.cvssScore !== null ? `CVSS ${item.cvssScore.toFixed(1)}` : "CVSS —"}
                <i />
                {item.epssScore !== null ? `EPSS ${percent(item.epssScore)}` : "EPSS —"}
                <i />
                {item.sourceName}
                <i />
                {formatDate(item.publishedAt, language, true)}
              </span>
            </button>
            <div className="vulnerability-flags">
              {item.cisaKev ? <span className="flag critical">KEV</span> : null}
              {item.knownExploited ? <span className="flag critical">{t.exploited}</span> : null}
              {item.knownRansomwareUse ? <span className="flag critical">{t.ransomware}</span> : null}
              {!attentionItem(item) ? <span className="flag neutral">{t.noConfirmed}</span> : null}
            </div>
          </article>
        ))}
        {!items.length ? <div className="empty-state">{t.empty}</div> : null}
      </div>
    </section>
  );
}

function SourcesView({
  data,
  language,
  now,
}: {
  data: DashboardData;
  language: Language;
  now: number | null;
}) {
  const t = COPY[language];
  const maxLatency = Math.max(...data.sourceHealth.map((source) => source.durationMs), 1);
  const currentSources = data.sourceHealth.filter((source) =>
    hasRecentHealthyRun(source, now),
  );
  const gapSources = data.sourceHealth.filter(
    (source) => !hasRecentHealthyRun(source, now),
  );
  const currentCore = currentSources.filter((source) => source.required).length;
  const currentOptional = currentSources.filter((source) => !source.required).length;
  return (
    <section className="view-section">
      <div className="view-heading">
        <div>
          <span className="eyebrow">{t.sourceHealth}</span>
          <h1>{t.sourceOperations}</h1>
          <p>{t.sourceIntro}</p>
        </div>
        <div className={`pipeline-state ${data.pipelineStatus}`}>
          <i /> {pipelineLabel(data.pipelineStatus, language)}
        </div>
      </div>
      <div className="source-summary-grid">
        <div className="summary-tile">
          <span>{t.required}</span>
          <strong>{data.sourceHealth.filter((source) => source.required).length}</strong>
          <small>{currentCore} {currentCore === 1 ? t.healthySingle : t.healthy}</small>
        </div>
        <div className="summary-tile">
          <span>{t.optionalLabel}</span>
          <strong>{data.sourceHealth.filter((source) => !source.required).length}</strong>
          <small>{currentOptional} {currentOptional === 1 ? t.healthySingle : t.healthy}</small>
        </div>
        <div className="summary-tile">
          <span>{t.received}</span>
          <strong>{compactNumber(data.sourceHealth.reduce((sum, source) => sum + source.itemsReceived, 0), language)}</strong>
          <small>{t.coverage}</small>
        </div>
        <div className="summary-tile">
          <span>{t.latency}</span>
          <strong>{(data.sourceHealth.reduce((sum, source) => sum + source.durationMs, 0) / 1000).toFixed(1)}s</strong>
          <small>{t.totalCollectorTime}</small>
        </div>
      </div>
      <section className="resilience-panel" aria-labelledby="resilience-title">
        <div className="resilience-heading">
          <span className="section-label" id="resilience-title">{t.resiliencePath}</span>
          <p>{t.resilienceText}</p>
        </div>
        <ol className="delivery-chain">
          {data.deliveryChain.map((attempt, index) => (
            <li className={attempt.status} key={attempt.id}>
              <span className="delivery-step">{String(index + 1).padStart(2, "0")}</span>
              <a href={attempt.url} target="_blank" rel="noreferrer">
                <strong>{deliveryLabel(attempt.id, language)}</strong>
                <small>{deliveryStatusLabel(attempt.status, language)}</small>
              </a>
            </li>
          ))}
        </ol>
      </section>
      <section className="coverage-audit" aria-labelledby="coverage-audit-title">
        <div className="coverage-audit-heading">
          <span className="section-label" id="coverage-audit-title">{t.coverageLimits}</span>
          <p>{t.coverageLimitsText}</p>
        </div>
        <div className="coverage-audit-grid">
          <article className="coverage-status available">
            <span>{t.whatWeSee}</span>
            <strong>{currentSources.length}</strong>
            <p>{currentSources.length === 1 ? t.currentSource : t.currentSources}</p>
          </article>
          <article className={`coverage-status ${gapSources.length ? "gap" : "available"}`}>
            <span>{t.intelligenceGaps}</span>
            <strong>{gapSources.length}</strong>
            <p>
              {gapSources.length
                ? gapSources.length === 1
                  ? t.gapSource
                  : t.gapSources
                : t.noGaps}
            </p>
            {gapSources.length ? <small>{gapSources.map((source) => source.label).join(" · ")}</small> : null}
          </article>
          <div className="coverage-lanes" aria-label={t.sourceUse}>
            {(["evidence", "expert", "community"] as SourceTrustLane[]).map((lane) => (
              <span className={`trust-lane ${lane}`} key={lane}>
                <i /> {trustLaneLabel(lane, language)}
              </span>
            ))}
            <p>{t.coverageCaveat}</p>
          </div>
        </div>
      </section>
      <div className="source-table" aria-label={t.sourceOperations}>
        <div className="source-table-head" aria-hidden="true">
          <span>{t.sources}</span>
          <span>{t.status}</span>
          <span>{t.received}</span>
          <span>{t.accepted}</span>
          <span>{t.latency}</span>
        </div>
        {data.sourceHealth.map((source) => {
          const profile = SOURCE_PROFILES[source.source];
          const isCurrent = hasRecentHealthyRun(source, now);
          return (
            <a
              className="source-table-row"
              href={SOURCE_URLS[source.source] ?? data.repositoryUrl}
              target="_blank"
              rel="noreferrer"
              key={source.source}
            >
              <span className="source-name-cell">
                <b>{SOURCE_SHORT_LABELS[source.source]?.slice(0, 2) ?? source.label.slice(0, 2)}</b>
                <span>
                  <strong>{source.label}</strong>
                  <small>
                    {source.required ? t.required : t.optionalLabel}
                    {profile ? ` · ${provenanceLabel(profile.provenance, language)}` : ""}
                  </small>
                  {profile ? (
                    <em className={`source-lane-label ${profile.lane}`}>
                      {trustLaneLabel(profile.lane, language)}
                    </em>
                  ) : null}
                </span>
              </span>
              <span className={`status-pill ${isCurrent ? "healthy" : source.status === "healthy" ? "degraded" : source.status}`}>
                <i /> {source.status === "healthy" ? sourceFreshnessLabel(source, language, now) : statusLabel(source.status, language)}
              </span>
              <strong>{source.itemsReceived.toLocaleString()}</strong>
              <strong>{source.itemsAccepted.toLocaleString()}</strong>
              <span className="latency-cell">
                <span className="latency-track">
                  <i style={{ width: `${Math.max(3, (source.durationMs / maxLatency) * 100)}%` }} />
                </span>
                <strong>{source.durationMs}ms</strong>
              </span>
            </a>
          );
        })}
      </div>
    </section>
  );
}

function MethodologyView({
  data,
  language,
}: {
  data: DashboardData;
  language: Language;
}) {
  const t = COPY[language];
  const phases = [
    [t.collection, t.collectionText, "01"],
    [t.normalization, t.normalizationText, "02"],
    [t.scoring, t.scoringText, "03"],
    [t.publication, t.publicationText, "04"],
  ];
  return (
    <section className="view-section methodology-view">
      <div className="view-heading">
        <div>
          <span className="eyebrow">{t.methodology}</span>
          <h1>{t.methodTitle}</h1>
          <p>{t.methodIntro}</p>
        </div>
        <a className="button primary compact" href={data.repositoryUrl} target="_blank" rel="noreferrer">
          <Icon name="github" size={18} /> {t.repo}
        </a>
      </div>
      <div className="method-phases">
        {phases.map(([title, text, number]) => (
          <article key={title}>
            <span>{number}</span>
            <h2>{title}</h2>
            <p>{text}</p>
          </article>
        ))}
      </div>
      <div className="method-grid">
        <article className="paper-panel trust-panel">
          <span className="section-label">{t.trustBoundaries}</span>
          <div>
            <span className="trust-number">01</span>
            <strong>{t.evidence}</strong>
            <p>{t.evidenceText}</p>
          </div>
          <div>
            <span className="trust-number">02</span>
            <strong>{t.expert}</strong>
            <p>{t.expertText}</p>
          </div>
          <div>
            <span className="trust-number">03</span>
            <strong>{t.communityLane}</strong>
            <p>{t.communityText}</p>
          </div>
        </article>
        <article className="paper-panel score-panel">
          <span className="section-label">{t.scoreLabel}</span>
          <div className="score-band-list">
            {data.scoreBands.map((band, index) => {
              const maximum = Math.max(...data.scoreBands.map((point) => point.count), 1);
              return (
                <div key={band.label}>
                  <span>{band.label}</span>
                  <span className="score-band-track">
                    <i
                      style={{
                        width: `${Math.max(4, (band.count / maximum) * 100)}%`,
                        background: index >= 4 ? "#c9342f" : index >= 2 ? "#f27622" : "#1747d1",
                      }}
                    />
                  </span>
                  <strong>{band.count}</strong>
                </div>
              );
            })}
          </div>
          <p>{t.scoreFormula}</p>
        </article>
      </div>
      <article className="portable-panel">
        <div>
          <span className="eyebrow">{t.portableEyebrow}</span>
          <h2>{t.portable}</h2>
          <p>{t.portableText}</p>
        </div>
        <div className="portable-actions">
          <a href={`${data.repositoryUrl}#run-locally`} target="_blank" rel="noreferrer">
            {t.runLocal} <Icon name="arrow" size={17} />
          </a>
          <a
            href="https://raw.githubusercontent.com/JimBLogic/CyberDailyLog/main/schemas/portfolio-feed.schema.json"
            target="_blank"
            rel="noreferrer"
          >
            {t.dataContract} <Icon name="arrow" size={17} />
          </a>
        </div>
      </article>
    </section>
  );
}

function EngineeringView({
  data,
  language,
}: {
  data: DashboardData;
  language: Language;
}) {
  const copy =
    language === "es"
      ? {
          eyebrow: "Reproducibilidad y DevSecOps",
          title: "Auditable desde el clon.",
          intro:
            "La calidad no depende de una demo bonita: el repositorio separa runtime, contratos, salidas e histórico, y valida un recorrido offline sin publicar nada.",
          openCi: "Ver CI",
          baseline: [
            ["Python", "3.12", "Runtime fijado"],
            ["Cobertura", "≥85 %", "El umbral no se rebaja"],
            ["Automatización", "2 ventanas", "08:17 + recuperación 09:47"],
            ["Modo local", "Offline", "Fixtures sin secretos ni publicación"],
          ],
          mapTitle: "Mapa autorizado del repositorio",
          map: [
            ["src/cyberdailylog/", "Runtime activo y lógica de publicación"],
            ["tests/", "Pruebas unitarias, contratos y regresiones"],
            ["config/", "Fuentes, priorización y configuración mantenida"],
            ["reports/", "Salidas actuales generadas del producto"],
            ["reports/archive/", "Histórico diario activo, no legado"],
            ["schemas/", "Contratos JSON públicos y versionados"],
            ["docs/", "Arquitectura, integración y operación"],
            ["legacy/personal-progress/", "Contexto conservado fuera del proceso"],
          ],
          guardTitle: "Invariantes de publicación",
          guards: [
            "La comprobación de frescura impide dos publicaciones del mismo día.",
            "El quorum obligatorio no se debilita y los fallos opcionales quedan visibles.",
            "El JSON completo conserva los registros aunque el resumen aplique umbral.",
            "El informe anterior se archiva antes de sustituir los archivos latest.",
            "CI y ejecución local no publican ni modifican main.",
            "No se ejecutan PoC, no se descarga malware y no se imprimen secretos.",
          ],
          matrixTitle: "Matriz real de validación",
          matrix:
            "Ruff lint + formato · MyPy · Pytest con cobertura · fixtures offline · JSON Schema · wheel smoke test · pip-audit · escaneo ligero de secretos",
          commandsTitle: "Clon limpio → informe offline validado",
          commandsNote:
            "Estos comandos generan en tmp/reports y no tocan los informes publicados.",
          historyTitle: "Dos archivos, dos responsabilidades",
          productHistory: "Histórico del producto",
          productHistoryText:
            "reports/archive/ participa en la trazabilidad diaria y nunca debe usarse como cajón de código viejo.",
          repoHistory: "Legado consultable",
          repoHistoryText:
            "archive/repository-history/ solo se crea si existe material útil que retirar; queda explícitamente fuera de runtime, CI y publicación.",
          currentSource: "Fuente autorizada",
          docs: "Abrir guía de integración",
        }
      : {
          eyebrow: "Reproducibility & DevSecOps",
          title: "Auditable from a fresh clone.",
          intro:
            "Quality does not depend on a polished demo: the repository separates runtime, contracts, outputs and history, then validates a fully offline path without publishing anything.",
          openCi: "Inspect CI",
          baseline: [
            ["Python", "3.12", "Pinned runtime"],
            ["Coverage", "≥85%", "The threshold is not lowered"],
            ["Automation", "2 windows", "08:17 + 09:47 recovery"],
            ["Local mode", "Offline", "Fixtures, no secrets or publishing"],
          ],
          mapTitle: "Authoritative repository map",
          map: [
            ["src/cyberdailylog/", "Active runtime and publication logic"],
            ["tests/", "Unit, contract and regression tests"],
            ["config/", "Maintained source and scoring configuration"],
            ["reports/", "Current generated product outputs"],
            ["reports/archive/", "Active daily history, not legacy"],
            ["schemas/", "Versioned public JSON contracts"],
            ["docs/", "Architecture, integration and operations"],
            ["legacy/personal-progress/", "Preserved context outside the pipeline"],
          ],
          guardTitle: "Publication invariants",
          guards: [
            "The freshness gate prevents two publications for one day.",
            "Required-source quorum stays strict; optional failures remain visible.",
            "The complete JSON keeps records even when the brief applies a threshold.",
            "The previous report is archived before latest files are replaced.",
            "CI and local runs never publish or mutate main.",
            "No PoC execution, malware download or secret output is allowed.",
          ],
          matrixTitle: "Real validation matrix",
          matrix:
            "Ruff lint + format · MyPy · Pytest with coverage · offline fixtures · JSON Schema · wheel smoke test · pip-audit · lightweight secret scan",
          commandsTitle: "Fresh clone → validated offline report",
          commandsNote:
            "These commands generate into tmp/reports and leave published reports untouched.",
          historyTitle: "Two archives, two responsibilities",
          productHistory: "Product history",
          productHistoryText:
            "reports/archive/ is part of daily traceability and must never become a dumping ground for old code.",
          repoHistory: "Consultable legacy",
          repoHistoryText:
            "archive/repository-history/ is created only when useful retired material exists; it stays outside runtime, CI and daily publication.",
          currentSource: "Authoritative source",
          docs: "Open integration guide",
        };
  const commands = `git clone https://github.com/JimBLogic/CyberDailyLog.git
cd CyberDailyLog
python -m venv .venv
# macOS / Linux:  . .venv/bin/activate
# Windows:        .venv\\Scripts\\activate
python -m pip install . -r requirements-dev.txt
make lint && make typecheck && make test
make offline-report && make validate
python -m cyberdailylog.portfolio_feed \\
  --report tmp/reports/latest.json \\
  --output tmp/reports/portfolio-feed.json`;

  return (
    <section className="view-section engineering-view">
      <div className="view-heading">
        <div>
          <span className="eyebrow">{copy.eyebrow}</span>
          <h1>{copy.title}</h1>
          <p>{copy.intro}</p>
        </div>
        <a
          className="button primary compact"
          href={`${data.repositoryUrl}/actions/workflows/ci.yml`}
          target="_blank"
          rel="noreferrer"
        >
          <Icon name="check" size={18} /> {copy.openCi}
        </a>
      </div>

      <div className="engineering-baseline">
        {copy.baseline.map(([label, value, note]) => (
          <article key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
            <small>{note}</small>
          </article>
        ))}
      </div>

      <div className="engineering-grid">
        <article className="paper-panel repository-map">
          <span className="section-label">{copy.mapTitle}</span>
          <div>
            {copy.map.map(([path, purpose]) => (
              <div key={path}>
                <code>{path}</code>
                <span>{purpose}</span>
              </div>
            ))}
          </div>
        </article>
        <article className="paper-panel invariant-panel">
          <span className="section-label">{copy.guardTitle}</span>
          <ol>
            {copy.guards.map((guard) => (
              <li key={guard}>
                <Icon name="check" size={16} />
                <span>{guard}</span>
              </li>
            ))}
          </ol>
          <div className="validation-matrix">
            <strong>{copy.matrixTitle}</strong>
            <p>{copy.matrix}</p>
          </div>
        </article>
      </div>

      <article className="command-panel">
        <div>
          <span className="eyebrow">{copy.commandsTitle}</span>
          <p>{copy.commandsNote}</p>
          <a
            href={`${data.repositoryUrl}/blob/main/docs/INTEGRATION.md`}
            target="_blank"
            rel="noreferrer"
          >
            {copy.docs} <Icon name="external" size={15} />
          </a>
        </div>
        <pre aria-label={copy.commandsTitle}>
          <code>{commands}</code>
        </pre>
      </article>

      <article className="archive-policy">
        <span className="section-label">{copy.historyTitle}</span>
        <div>
          <section>
            <span>ACTIVE</span>
            <h2>{copy.productHistory}</h2>
            <code>reports/archive/</code>
            <p>{copy.productHistoryText}</p>
          </section>
          <section>
            <span>NON-RUNTIME</span>
            <h2>{copy.repoHistory}</h2>
            <code>archive/repository-history/</code>
            <p>{copy.repoHistoryText}</p>
          </section>
        </div>
        <a href={data.repositoryUrl} target="_blank" rel="noreferrer">
          {copy.currentSource} <Icon name="github" size={16} />
        </a>
      </article>
    </section>
  );
}

function DetailDialog({
  item,
  language,
  onClose,
  watched,
  onWatchlist,
}: {
  item: Vulnerability;
  language: Language;
  onClose: () => void;
  watched: boolean;
  onWatchlist: () => void;
}) {
  const t = COPY[language];
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    document.body.classList.add("modal-open");
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.classList.remove("modal-open");
    };
  }, [onClose]);

  return (
    <div className="dialog-backdrop" role="presentation" onMouseDown={onClose}>
      <section
        className="detail-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="dialog-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="dialog-header">
          <div>
            <span className={`severity-pill ${severityClass(item.severity)}`}>
              {severityLabel(item.severity, language)}
            </span>
            <h2 id="dialog-title">{item.id}</h2>
          </div>
          <div>
            <button
              className={`icon-button ${watched ? "active" : ""}`}
              onClick={onWatchlist}
              aria-label={watched ? t.unwatch : t.watch}
            >
              <Icon name="star" />
            </button>
            <button className="icon-button" onClick={onClose} aria-label={t.close} autoFocus>
              <Icon name="x" />
            </button>
          </div>
        </div>
        <div className="dialog-scoreline">
          <div>
            <span>{t.priority}</span>
            <strong>{item.priorityScore.toFixed(1)}</strong>
          </div>
          <div>
            <span>CVSS</span>
            <strong>{item.cvssScore?.toFixed(1) ?? "—"}</strong>
          </div>
          <div>
            <span>EPSS</span>
            <strong>{percent(item.epssScore)}</strong>
          </div>
          <div>
            <span>CISA KEV</span>
            <strong>{item.cisaKev ? t.yes : t.no}</strong>
          </div>
        </div>
        <div className="dialog-body">
          <h3>{item.title}</h3>
          <p className="dialog-summary">{item.summary}</p>
          <div className="dialog-section">
            <span>{t.reasons}</span>
            <ul>
              {(item.reasons.length ? item.reasons : [t.sourceBackedFallback]).map((reason) => (
                <li key={reason}><Icon name="check" size={16} />{localizedReason(reason, language)}</li>
              ))}
            </ul>
          </div>
          <div className="dialog-section">
            <span>{t.actions}</span>
            <ul>
              {(item.actions.length
                ? item.actions
                : [t.inventoryFallback]
              ).map((action) => (
                <li key={action}><Icon name="shield" size={16} />{localizedAction(action, language)}</li>
              ))}
            </ul>
          </div>
          {item.references.length ? (
            <div className="dialog-section">
              <span>{t.references}</span>
              <div className="reference-links">
                {item.references.map((reference, index) => (
                  <a href={reference} target="_blank" rel="noreferrer" key={reference}>
                    {t.reference} {index + 1} <Icon name="external" size={14} />
                  </a>
                ))}
              </div>
            </div>
          ) : null}
        </div>
        <div className="dialog-footer">
          <span>{item.sourceName} · {formatDate(item.publishedAt, language)}</span>
          <a className="button primary compact" href={item.sourceUrl} target="_blank" rel="noreferrer">
            {t.primarySource} <Icon name="external" size={16} />
          </a>
        </div>
      </section>
    </div>
  );
}

export function Dashboard({ initialData }: { initialData: DashboardData }) {
  const [data, setData] = useState(initialData);
  const [view, setView] = useState<View>("overview");
  const [language, setLanguage] = useState<Language>("es");
  const [selected, setSelected] = useState<Vulnerability | null>(null);
  const [watchlist, setWatchlist] = useState<Set<string>>(new Set());
  const [refreshing, setRefreshing] = useState(false);
  const [notice, setNotice] = useState("");
  const [clock, setClock] = useState<number | null>(null);
  const t = COPY[language];

  useEffect(() => {
    const frame = window.requestAnimationFrame(() => {
      const storedLanguage = readLocalPreference(
        "cyberdailylog-language",
      );
      const storedWatchlist = readLocalPreference(
        "cyberdailylog-watchlist",
      );
      if (storedLanguage === "en" || storedLanguage === "es") {
        setLanguage(storedLanguage);
      }
      const hashView = window.location.hash.slice(1) as View;
      if (VIEW_KEYS.includes(hashView)) setView(hashView);
      if (storedWatchlist) {
        try {
          setWatchlist(new Set(JSON.parse(storedWatchlist) as string[]));
        } catch {
          removeLocalPreference("cyberdailylog-watchlist");
        }
      }
    });
    return () => window.cancelAnimationFrame(frame);
  }, []);

  useEffect(() => {
    const syncView = () => {
      const hashView = window.location.hash.slice(1) as View;
      setView(VIEW_KEYS.includes(hashView) ? hashView : "overview");
    };
    window.addEventListener("hashchange", syncView);
    return () => window.removeEventListener("hashchange", syncView);
  }, []);

  useEffect(() => {
    const initialTick = window.setTimeout(() => setClock(Date.now()), 0);
    const timer = window.setInterval(() => setClock(Date.now()), 1_000);
    return () => {
      window.clearTimeout(initialTick);
      window.clearInterval(timer);
    };
  }, []);

  function changeLanguage(next: Language) {
    setLanguage(next);
    writeLocalPreference("cyberdailylog-language", next);
  }

  function toggleWatchlist(id: string) {
    setWatchlist((current) => {
      const next = new Set(current);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      writeLocalPreference(
        "cyberdailylog-watchlist",
        JSON.stringify([...next]),
      );
      return next;
    });
  }

  const refreshData = useCallback(async (showNotice = true) => {
    setRefreshing(true);
    if (showNotice) setNotice("");
    try {
      const response = await fetch("/api/intelligence", {
        cache: "no-store",
      });
      if (!response.ok) throw new Error("refresh failed");
      const next = (await response.json()) as DashboardData;
      setData(next);
      if (showNotice) {
        setNotice(
          next.dataMode === "repository-snapshot" ? t.fallbackRetained : t.refreshed,
        );
      }
    } catch {
      if (showNotice) setNotice(t.refreshFailed);
    } finally {
      setRefreshing(false);
      if (showNotice) window.setTimeout(() => setNotice(""), 4_000);
    }
  }, [t.fallbackRetained, t.refreshFailed, t.refreshed]);

  useEffect(() => {
    const target = parseTimestamp(data.nextRefreshAt);
    const delay = target !== null
      ? Math.max(5_000, target - Date.now() + 1_000)
      : 60_000;
    const timer = window.setTimeout(() => {
      void refreshData(false);
    }, Math.min(delay, 2_147_000_000));
    return () => window.clearTimeout(timer);
  }, [data.nextRefreshAt, refreshData]);

  function navigate(next: View) {
    setView(next);
    const nextHash = next === "overview" ? window.location.pathname : `#${next}`;
    window.history.pushState(null, "", nextHash);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  const topItem = data.vulnerabilities[0];
  const tabs: Array<[View, string]> = [
    ["overview", t.overview],
    ["vulnerabilities", t.vulnerabilities],
    ["sources", t.sources],
    ["methodology", t.methodology],
    ["engineering", t.engineering],
  ];

  return (
    <>
      <a className="skip-link" href="#main-content">
        {language === "es" ? "Saltar al contenido" : "Skip to content"}
      </a>
      <main className="site-shell" id="main-content">
      <header className="masthead">
        <button type="button" className="wordmark" onClick={() => navigate("overview")}>
          CyberDailyLog
        </button>
        <nav aria-label={t.primaryNavigation}>
          {tabs.map(([key, label]) => (
            <button
              type="button"
              className={view === key ? "active" : ""}
              onClick={() => navigate(key)}
              aria-current={view === key ? "page" : undefined}
              key={key}
            >
              {label}
            </button>
          ))}
        </nav>
        <div className="masthead-meta">
          <span className="date-chip">
            <Icon name="calendar" size={19} />
            {formatDate(data.generatedAt, language, true)}
          </span>
          <span className="briefing-chip">
            <span aria-hidden="true">☼</span>
            {t.morning}
          </span>
          <span className="language-toggle" role="group" aria-label={t.language}>
            <button
              type="button"
              className={language === "en" ? "active" : ""}
              aria-label="English"
              aria-pressed={language === "en"}
              onClick={() => changeLanguage("en")}
            >
              EN
            </button>
            <button
              type="button"
              className={language === "es" ? "active" : ""}
              aria-label="Español"
              aria-pressed={language === "es"}
              onClick={() => changeLanguage("es")}
            >
              ES
            </button>
          </span>
          <button
            type="button"
            className="refresh-button"
            onClick={() => void refreshData(true)}
            disabled={refreshing}
            aria-label={refreshing ? t.refreshing : t.refresh}
            title={refreshing ? t.refreshing : t.refresh}
          >
            <span className={refreshing ? "spinning" : ""}><Icon name="refresh" size={18} /></span>
          </button>
        </div>
      </header>

      {notice ? <div className="toast" role="status">{notice}</div> : null}

      <FreshnessBanner
        data={data}
        language={language}
        now={clock}
        refreshing={refreshing}
        onRefresh={() => void refreshData(true)}
      />

      {view === "overview" ? (
        <div className="overview-view">
          <section className="hero-grid">
            <div className="hero-left">
              <div className="hero-top">
                <div className="hero-copy">
                  <span className="eyebrow">{t.eyebrow}</span>
                  <h1>
                    {t.heroA}
                    <br />
                    {t.heroB}
                  </h1>
                  <p>{t.heroText}</p>
                  <div className="hero-actions">
                    <button className="button primary" onClick={() => navigate("vulnerabilities")}>
                      <Icon name="database" /> {t.openBrief}
                    </button>
                    <button className="button secondary" onClick={() => navigate("methodology")}>
                      <span className="button-info">i</span> {t.how}
                    </button>
                  </div>
                </div>
                <div className="pipeline-wrap">
                  <Pipeline
                    language={language}
                    status={data.pipelineStatus}
                    dataMode={data.dataMode}
                  />
                  <DataDelivery data={data} language={language} now={clock} />
                </div>
              </div>
              <RiskDistribution data={data} language={language} />
            </div>
            {topItem ? (
              <PriorityCard item={topItem} language={language} onOpen={() => setSelected(topItem)} />
            ) : null}
          </section>
          <MetricStrip data={data} language={language} />
          <SourceRail sources={data.sourceHealth} language={language} now={clock} />
          <div className="below-fold-grid">
            <HistoryChart
              history={
                data.dataMode === "live" ? data.history : data.history.slice(-1)
              }
              language={language}
            />
            <aside className="attention-panel">
              <span className="section-label">{t.immediateAttention}</span>
              <strong>{data.immediateAttentionCount}</strong>
              <p>
                {data.immediateAttentionCount
                  ? `${data.immediateAttentionCount} ${t.immediateCount}`
                  : t.noImmediate}
              </p>
              <button onClick={() => navigate("vulnerabilities")}>
                {t.openBrief} <Icon name="arrow" size={17} />
              </button>
            </aside>
          </div>
          <SignalDesk data={data} language={language} />
          <InterviewProof data={data} language={language} />
          <footer className="dashboard-footer">
            <span>
              {t.published}: {formatDate(data.generatedAt, language)} UTC
            </span>
            <span>
              {t.fetched}: {formatDate(data.lastFetchAt, language)} UTC
            </span>
            <a href={data.repositoryUrl} target="_blank" rel="noreferrer">
              <Icon name="github" size={16} /> JimBLogic/CyberDailyLog
            </a>
          </footer>
        </div>
      ) : null}

      {view === "vulnerabilities" ? (
        <VulnerabilityList
          data={data}
          language={language}
          watchlist={watchlist}
          onWatchlist={toggleWatchlist}
          onOpen={setSelected}
        />
      ) : null}
      {view === "sources" ? <SourcesView data={data} language={language} now={clock} /> : null}
      {view === "methodology" ? <MethodologyView data={data} language={language} /> : null}
      {view === "engineering" ? <EngineeringView data={data} language={language} /> : null}

      {selected ? (
        <DetailDialog
          item={selected}
          language={language}
          watched={watchlist.has(selected.id)}
          onWatchlist={() => toggleWatchlist(selected.id)}
          onClose={() => setSelected(null)}
        />
      ) : null}
      </main>
    </>
  );
}
