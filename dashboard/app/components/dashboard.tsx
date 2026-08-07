"use client";

import { useEffect, useMemo, useState } from "react";
import { SOURCE_SHORT_LABELS, SOURCE_URLS } from "@/lib/source-labels";
import type {
  DashboardData,
  HistoryPoint,
  Severity,
  SourceHealth,
  Vulnerability,
} from "@/lib/types";

type View = "overview" | "vulnerabilities" | "sources" | "methodology";
type Language = "en" | "es";

const COPY = {
  en: {
    overview: "Overview",
    vulnerabilities: "Vulnerabilities",
    sources: "Sources",
    methodology: "Methodology",
    morning: "Morning threat briefing",
    eyebrow: "Daily Blue Team intelligence",
    heroA: "Intelligence today.",
    heroB: "Protection ahead.",
    heroText:
      "CyberDailyLog turns trusted vulnerability feeds and analyst sources into a prioritized morning briefing so defenders can act first.",
    openBrief: "Open today’s brief",
    how: "How it works",
    operational: "Operational pipeline",
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
    riskDistribution: "Risk distribution",
    total: "of security items",
    sourceHealth: "Source health",
    sourceFreshness: "Freshness reflects the latest collector run",
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
    refreshed: "Dashboard refreshed from the repository.",
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
  },
  es: {
    overview: "Resumen",
    vulnerabilities: "Vulnerabilidades",
    sources: "Fuentes",
    methodology: "Metodología",
    morning: "Briefing matinal de amenazas",
    eyebrow: "Inteligencia Blue Team diaria",
    heroA: "Inteligencia hoy.",
    heroB: "Protección por delante.",
    heroText:
      "CyberDailyLog convierte fuentes fiables de vulnerabilidades y análisis en un briefing priorizado para que el defensor actúe primero.",
    openBrief: "Abrir briefing de hoy",
    how: "Cómo funciona",
    operational: "Pipeline operativo",
    collect: "Recopilar",
    normalize: "Normalizar",
    score: "Puntuar",
    publish: "Publicar",
    live: "Activo",
    updated: "Actualizado",
    coverage: "Cobertura de 24 horas",
    topPriority: "Máxima prioridad",
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
    riskDistribution: "Distribución del riesgo",
    total: "de elementos de seguridad",
    sourceHealth: "Salud de las fuentes",
    sourceFreshness: "La frescura refleja la última ejecución",
    historical: "Señal de ocho días",
    historicalText:
      "Volumen diario, elementos de alto impacto y estado del pipeline desde el archivo.",
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
    methodTitle: "Transparente por diseño",
    methodIntro:
      "Un pipeline reproducible que mantiene afirmaciones, contexto e interés comunitario en carriles de confianza separados.",
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
      "Briefing, evidencia completa, feed compacto, salud de fuentes y archivo se validan antes de publicarse.",
    trustBoundaries: "Límites de confianza",
    evidence: "Evidencia",
    evidenceText: "CVE, KEV, EPSS y avisos oficiales.",
    expert: "Contexto experto",
    expertText: "Extractos breves y atribuidos de editores permitidos.",
    communityLane: "Señal comunitaria",
    communityText: "El engagement nunca se presenta como riesgo verificado.",
    portable: "Un proyecto, dos superficies útiles",
    portableText:
      "El repositorio continúa siendo ejecutable por sí solo. Su JSON alimenta este backend y el código del dashboard vuelve al repositorio para usarlo localmente o en otro hosting.",
    repo: "Abrir repositorio",
    runLocal: "Instrucciones autónomas",
    dataContract: "Inspeccionar contrato JSON",
    close: "Cerrar",
    references: "Referencias",
    reasons: "Razones de prioridad",
    actions: "Acciones recomendadas",
    published: "Publicado",
    fetched: "Consulta del dashboard",
    dataMode: "Fuente de datos",
    liveRepo: "Datos vivos del repositorio",
    snapshot: "Snapshot verificado de respaldo",
    refreshing: "Actualizando…",
    refresh: "Actualizar datos",
    refreshFailed: "Falló la actualización; se mantiene el snapshot verificado.",
    refreshed: "Dashboard actualizado desde el repositorio.",
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
    signalDesk: "Mesa de señales",
    signalDeskTitle: "Más que CVE: la lectura del analista para hoy",
    signalDeskText:
      "Diarios operativos y pistas de la comunidad recopilados en la misma ejecución, separados claramente por nivel de evidencia.",
    analystBriefs: "Briefings de analistas y editores",
    communitySignals: "Señales de la comunidad",
    originalSource: "Contenido original de la fuente",
    originalSourceNote:
      "Los títulos y extractos se mantienen en el idioma original del editor para preservar su precisión.",
    viewSignal: "Abrir señal",
    interviewEyebrow: "Proof of Work para entrevistas",
    interviewTitle: "No me limité a seguir las noticias. Construí el workflow.",
    interviewQuote:
      "Cuando me preguntan dónde me mantengo al día, CyberDailyLog es mi respuesta: un pipeline Blue Team reproducible que recopila, valida, prioriza y publica un briefing diario.",
    proofProblem: "Problema",
    proofProblemText:
      "La información de seguridad está fragmentada, genera ruido y cuesta convertirla en una rutina diaria defendible.",
    proofBuild: "Construcción",
    proofBuildText:
      "Recopiladores Python, scoring determinista, controles de salud, pruebas y GitHub Actions.",
    proofResult: "Resultado",
    proofResultText:
      "Briefing matinal trazable, dashboard de analista, JSON integrable e histórico verificable.",
    dailyAutomation: "Automatización diaria",
    primaryRun: "Ejecución principal",
    recoveryRun: "Ejecución de recuperación",
    madridTime: "Europa/Madrid",
    generatedOutputs: "Salidas validadas",
    outputKinds: "MD · JSON · API · SALUD · HISTÓRICO",
    openWorkflow: "Inspeccionar workflow de GitHub",
    portableEyebrow: "GitHub ↔ Dashboard full-stack",
    sourceBackedFallback: "Relevancia defensiva respaldada por la fuente",
    inventoryFallback:
      "Inventaría los productos afectados, verifica la exposición y sigue las indicaciones del proveedor.",
  },
} as const;

const SEVERITY_ORDER: Severity[] = [
  "CRITICAL",
  "HIGH",
  "MEDIUM",
  "LOW",
  "UNKNOWN",
];

function formatDate(value: string, language: Language, short = false) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  return new Intl.DateTimeFormat(language === "es" ? "es-ES" : "en-GB", {
    day: "2-digit",
    month: short ? "short" : "long",
    year: "numeric",
    ...(short ? {} : { hour: "2-digit", minute: "2-digit" }),
    timeZone: "UTC",
  }).format(date);
}

function formatRelative(value: string, language: Language) {
  const milliseconds = Date.now() - new Date(value).getTime();
  if (!Number.isFinite(milliseconds)) return "—";
  const minutes = Math.max(0, Math.round(milliseconds / 60_000));
  if (minutes < 60) return language === "es" ? `hace ${minutes} min` : `${minutes}m ago`;
  const hours = Math.round(minutes / 60);
  if (hours < 48) return language === "es" ? `hace ${hours} h` : `${hours}h ago`;
  const days = Math.round(hours / 24);
  return language === "es" ? `hace ${days} d` : `${days}d ago`;
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

function Pipeline({ language }: { language: Language }) {
  const t = COPY[language];
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
            <small>{t.live}</small>
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
}: {
  sources: SourceHealth[];
  language: Language;
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
                  ? formatRelative(source.finishedAt, language)
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
}: {
  data: DashboardData;
  language: Language;
}) {
  const t = COPY[language];
  const maxLatency = Math.max(...data.sourceHealth.map((source) => source.durationMs), 1);
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
          <small>{data.sourceHealth.filter((source) => source.required && source.status === "healthy").length} {t.healthy}</small>
        </div>
        <div className="summary-tile">
          <span>{t.optionalLabel}</span>
          <strong>{data.sourceHealth.filter((source) => !source.required).length}</strong>
          <small>{data.sourceHealth.filter((source) => !source.required && source.status === "healthy").length} {t.healthy}</small>
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
      <div className="source-table" role="table" aria-label={t.sourceOperations}>
        <div className="source-table-head" role="row">
          <span>{t.sources}</span>
          <span>{t.status}</span>
          <span>{t.received}</span>
          <span>{t.accepted}</span>
          <span>{t.latency}</span>
        </div>
        {data.sourceHealth.map((source) => (
          <a
            className="source-table-row"
            role="row"
            href={SOURCE_URLS[source.source] ?? "#"}
            target="_blank"
            rel="noreferrer"
            key={source.source}
          >
            <span className="source-name-cell">
              <b>{SOURCE_SHORT_LABELS[source.source]?.slice(0, 2) ?? source.label.slice(0, 2)}</b>
              <span>
                <strong>{source.label}</strong>
                <small>{source.required ? t.required : t.optionalLabel}</small>
              </span>
            </span>
            <span className={`status-pill ${source.status}`}>
              <i /> {statusLabel(source.status, language)}
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
        ))}
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
  const [language, setLanguage] = useState<Language>("en");
  const [selected, setSelected] = useState<Vulnerability | null>(null);
  const [watchlist, setWatchlist] = useState<Set<string>>(new Set());
  const [refreshing, setRefreshing] = useState(false);
  const [notice, setNotice] = useState("");
  const t = COPY[language];

  useEffect(() => {
    const frame = window.requestAnimationFrame(() => {
      const storedLanguage = window.localStorage.getItem(
        "cyberdailylog-language",
      );
      const storedWatchlist = window.localStorage.getItem(
        "cyberdailylog-watchlist",
      );
      if (storedLanguage === "en" || storedLanguage === "es") {
        setLanguage(storedLanguage);
      }
      if (storedWatchlist) {
        try {
          setWatchlist(new Set(JSON.parse(storedWatchlist) as string[]));
        } catch {
          window.localStorage.removeItem("cyberdailylog-watchlist");
        }
      }
    });
    return () => window.cancelAnimationFrame(frame);
  }, []);

  function changeLanguage(next: Language) {
    setLanguage(next);
    window.localStorage.setItem("cyberdailylog-language", next);
  }

  function toggleWatchlist(id: string) {
    setWatchlist((current) => {
      const next = new Set(current);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      window.localStorage.setItem(
        "cyberdailylog-watchlist",
        JSON.stringify([...next]),
      );
      return next;
    });
  }

  async function refreshData() {
    setRefreshing(true);
    setNotice("");
    try {
      const response = await fetch(`/api/intelligence?refresh=${Date.now()}`, {
        cache: "no-store",
      });
      if (!response.ok) throw new Error("refresh failed");
      const next = (await response.json()) as DashboardData;
      setData(next);
      setNotice(t.refreshed);
    } catch {
      setNotice(t.refreshFailed);
    } finally {
      setRefreshing(false);
      window.setTimeout(() => setNotice(""), 4_000);
    }
  }

  function navigate(next: View) {
    setView(next);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  const topItem = data.vulnerabilities[0];
  const tabs: Array<[View, string]> = [
    ["overview", t.overview],
    ["vulnerabilities", t.vulnerabilities],
    ["sources", t.sources],
    ["methodology", t.methodology],
  ];

  return (
    <main className="site-shell">
      <header className="masthead">
        <button className="wordmark" onClick={() => navigate("overview")}>
          CyberDailyLog
        </button>
        <nav aria-label={t.primaryNavigation}>
          {tabs.map(([key, label]) => (
            <button
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
          <span className="language-toggle" aria-label={t.language}>
            <button className={language === "en" ? "active" : ""} onClick={() => changeLanguage("en")}>EN</button>
            <button className={language === "es" ? "active" : ""} onClick={() => changeLanguage("es")}>ES</button>
          </span>
          <button
            className="refresh-button"
            onClick={refreshData}
            disabled={refreshing}
            aria-label={refreshing ? t.refreshing : t.refresh}
            title={refreshing ? t.refreshing : t.refresh}
          >
            <span className={refreshing ? "spinning" : ""}><Icon name="refresh" size={18} /></span>
          </button>
        </div>
      </header>

      {notice ? <div className="toast" role="status">{notice}</div> : null}

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
                  <Pipeline language={language} />
                  <div className="freshness-row">
                    <span>◷ {t.updated} {formatRelative(data.generatedAt, language)}</span>
                    <span>◴ {t.coverage}</span>
                  </div>
                  <div className={`data-mode ${data.dataMode}`}>
                    <i />
                    <span>
                      {data.dataMode === "live" ? t.liveRepo : t.snapshot}
                    </span>
                  </div>
                </div>
              </div>
              <RiskDistribution data={data} language={language} />
            </div>
            {topItem ? (
              <PriorityCard item={topItem} language={language} onOpen={() => setSelected(topItem)} />
            ) : null}
          </section>
          <MetricStrip data={data} language={language} />
          <SourceRail sources={data.sourceHealth} language={language} />
          <div className="below-fold-grid">
            <HistoryChart history={data.history} language={language} />
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
      {view === "sources" ? <SourcesView data={data} language={language} /> : null}
      {view === "methodology" ? <MethodologyView data={data} language={language} /> : null}

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
  );
}
