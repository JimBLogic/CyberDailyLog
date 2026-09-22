import type { DashboardData, Vulnerability } from "../../lib/types";
import { CHANGE_LABELS, type CtiState } from "../../lib/cti";

type Language = "es" | "en";
const timestamp = (value: string | null | undefined, language: Language) => value
  ? new Intl.DateTimeFormat(language === "es" ? "es-ES" : "en-GB", { timeZone: "Europe/Madrid", dateStyle: "short", timeStyle: "short" }).format(new Date(value))
  : "—";
const preciseTimestamp = (value: string | null | undefined, language: Language) => value
  ? new Intl.DateTimeFormat(language === "es" ? "es-ES" : "en-GB", { timeZone: "Europe/Madrid", dateStyle: "short", timeStyle: "medium" }).format(new Date(value))
  : "—";
const seconds = (value: number | null | undefined) => value == null ? "—" : value.toLocaleString(undefined, {maximumFractionDigits: 1}) + " s";
const madridParts = (value: number) => {
  const parts = new Intl.DateTimeFormat("en-CA", {timeZone:"Europe/Madrid",year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",hourCycle:"h23"}).formatToParts(new Date(value));
  const get = (type: string) => parts.find(part => part.type === type)?.value ?? "";
  return {day: [get("year"),get("month"),get("day")].join("-"), hour: Number(get("hour"))};
};

export function OperationalStatus({data, language, now}: {data: DashboardData; language: Language; now: number | null}) {
  const es = language === "es";
  const p = data.publicationReliability;
  const current = now ? madridParts(now) : null;
  const measured = p?.scheduledFor ? madridParts(Date.parse(p.scheduledFor)) : null;
  const missingToday = Boolean(current && measured && current.day > measured.day && current.hour >= 13);
  const status = missingToday ? "stale" : p?.status ?? "unknown";
  const labels: Record<string, string> = es
    ? {on_time:"En plazo",delayed:"Con retraso",stale:"Fuera de plazo",failed:"Fallida",unknown:"Sin medición",skipped:"Omitido: informe ya publicado"}
    : {on_time:"On time",delayed:"Delayed",stale:"Overdue",failed:"Failed",unknown:"Not measured",skipped:"Skipped: report already published"};
  const causes: Record<string, string> = es
    ? {scheduler:"Antes de crear la ejecución",dispatch:"Entre solicitud y creación",workflow_queue:"Cola de ejecución",pipeline:"Recogida y generación",publication:"Publicación",within_threshold:"Dentro del objetivo",unknown:"Origen sin determinar"}
    : {scheduler:"Before workflow creation",dispatch:"Between request and creation",workflow_queue:"Workflow queue",pipeline:"Collection and generation",publication:"Publication",within_threshold:"Within objective",unknown:"Cause undetermined"};
  const origins: Record<string, string> = es
    ? {external_push:"Solicitud externa",external:"Solicitud externa",schedule:"Cron de GitHub",manual:"Manual",workflow_dispatch:"Manual",push:"Cambio en el repositorio",unknown:"Sin identificar"}
    : {external_push:"External request",external:"External request",schedule:"GitHub cron",manual:"Manual",workflow_dispatch:"Manual",push:"Repository change",unknown:"Unidentified"};
  const attempt = p?.lastAttempt;
  const optional = data.sourceHealth.filter(source => !source.required);
  const gaps = optional.filter(source => source.status !== "healthy" || !source.finishedAt || (now && now - Date.parse(source.finishedAt) > 36 * 3_600_000));
  const cti = data.ctiSummary;
  return <section className="paper-panel operational-panel" aria-label={es ? "Inteligencia y puntualidad" : "Intelligence and timeliness"}>
    <div className="panel-heading">
      <span className="section-label">{es ? "Puntualidad de publicación" : "Publication timeliness"}</span>
      <strong className={status === "on_time" ? "operational-good" : "operational-note"}>{labels[status]}</strong>
    </div>
    <div className="operational-grid">
      <div><span>{es ? "Objetivo diario" : "Daily target"}</span><strong>12:00 Europe/Madrid</strong><small>{es ? "≥95 % en un máximo de 60 min" : "≥95% within 60 minutes"}</small></div>
      <div><span>{es ? "Última publicación medida" : "Last measured publication"}</span><strong>{timestamp(p?.actual, language)}</strong><small>{es ? "Prevista: " : "Scheduled: "}{timestamp(p?.scheduledFor, language)}</small></div>
      <div><span>{es ? "Retraso medido" : "Measured delay"}</span><strong>{p?.lagSeconds != null ? (p.lagSeconds / 60).toFixed(1) + " min" : "—"}</strong><small>{causes[p?.rootCause ?? "unknown"]}</small></div>
      <div><span>{es ? "SLO · ventana de 30 días" : "SLO · 30-day window"}</span><strong>{p?.sloPercentage != null ? p.sloPercentage.toFixed(1) + "%" : "—"}</strong><small>{p?.measuredDays ?? 0} {es ? "días medidos" : "days measured"} · {p?.fullWindow ? (es ? "ventana completa" : "full window") : (es ? "muestra parcial" : "partial sample")}</small></div>
    </div>
    <p className="operational-caption">
      {missingToday ? (es ? "No hay medición publicada para el objetivo de hoy. " : "No published measurement for today's target. ") : ""}
      {es ? "El SLO corresponde a la evaluación del " : "SLO evaluated at "}{timestamp(p?.evaluatedAt, language)}.
      {" "}{es ? "Mide publicación en GitHub; el panel comprueba novedades cada 15 min." : "Measures GitHub publication; the dashboard checks updates every 15 minutes."}
      {p?.runUrl ? <> <a href={p.runUrl} target="_blank" rel="noreferrer">{es ? "Ver evidencia" : "View evidence"} ↗</a></> : null}
    </p>
    {p ? <details className="publication-evidence">
      <summary>{es ? "Cronología y último intento" : "Timeline and latest attempt"}</summary>
      <p>{es ? "Origen de la publicación: " : "Publication trigger: "}{origins[p.origin]} · Europe/Madrid</p>
      <table><caption>{es ? "Hitos de la publicación medida" : "Measured publication milestones"}</caption><tbody>
        {[
          [es ? "Objetivo" : "Target", preciseTimestamp(p.scheduledFor, language)],
          [es ? "Solicitud externa" : "External request", preciseTimestamp(p.requestedAt, language)],
          [es ? "Workflow creado" : "Workflow created", preciseTimestamp(p.workflowCreated, language)],
          [es ? "Workflow iniciado" : "Workflow started", preciseTimestamp(p.workflowStarted, language)],
          [es ? "Publicación completada" : "Publication completed", preciseTimestamp(p.actual, language)],
          [es ? "Objetivo → solicitud" : "Target → request", seconds(p.requestLagSeconds)],
          [es ? "Solicitud → creación" : "Request → creation", seconds(p.dispatchSeconds)],
          [es ? "Cola del workflow" : "Workflow queue", seconds(p.queueSeconds)],
          [es ? "Recogida de fuentes" : "Source collection", seconds(p.fetchSeconds)],
        ].map(([label, value]) => <tr key={label}><th scope="row">{label}</th><td>{value}</td></tr>)}
      </tbody></table>
      {attempt ? <p><strong>{es ? "Último intento: " : "Latest attempt: "}{labels[attempt.status]}</strong><br />
        {origins[attempt.origin]} · {preciseTimestamp(attempt.created, language)}.
        {attempt.creationLagSeconds != null ? <> {es ? "Retraso hasta su creación: " : "Delay before creation: "}{(attempt.creationLagSeconds / 60).toFixed(1)} min.</> : null}
        {attempt.status === "skipped" ? <> {es ? "Este intento no cuenta como otra publicación ni mejora el SLO." : "This attempt is not another publication and does not improve the SLO."}</> : null}
        {attempt.runUrl ? <> <a href={attempt.runUrl} target="_blank" rel="noreferrer">{es ? "Ver intento" : "View attempt"} ↗</a></> : null}
      </p> : null}
    </details> : null}
    <div className="operational-grid cti-totals">
      <div><span>{es ? "CVE nuevas observadas" : "Newly observed CVEs"}</span><strong>{cti?.newVulnerabilities ?? "—"}</strong></div>
      <div><span>{es ? "CVE con cambios de estado" : "CVEs with state changes"}</span><strong>{cti?.stateChanges ?? "—"}</strong></div>
      <div><span>{es ? "Transiciones a KEV" : "KEV transitions"}</span><strong>{cti?.kev ?? "—"}</strong></div>
      <div><span>{es ? "Transiciones a ransomware" : "Ransomware transitions"}</span><strong>{cti?.ransomware ?? "—"}</strong></div>
    </div>
    <p className="operational-caption">{cti
      ? (es ? "Los cambios materiales vuelven a aparecer; las CVE sin cambios no se repiten como novedad." : "Material changes are surfaced again; unchanged CVEs are not repeated as new intelligence.")
      : (es ? "El informe mostrado aún no incluye comparación de estados. No se presupone que haya cero cambios." : "This report has no state comparison. Missing measurement does not mean zero changes.")}</p>
    <p className="operational-caption"><strong>{gaps.length ? (es ? "Enriquecimiento parcial" : "Partial enrichment") : optional.length ? (es ? "Enriquecimiento disponible" : "Enrichment available") : (es ? "Enriquecimiento sin medir" : "Enrichment not measured")}</strong>
      {gaps.length ? ": " + gaps.map(source => source.label).join(" · ") : ""}.
      {" "}{es ? "La salud de las fuentes core se muestra por separado." : "Core source health is reported separately."}</p>
  </section>;
}

function stateSummary(state: CtiState["current"], language: Language) {
  const es = language === "es";
  const status: Record<string, string> = es
    ? {unknown:"Explotación desconocida",no_known_evidence:"Sin evidencia conocida de explotación",confirmed_not_exploited:"Ausencia de explotación confirmada por la fuente",confirmed_exploitation:"Explotación confirmada"}
    : {unknown:"Exploitation unknown",no_known_evidence:"No known exploitation evidence",confirmed_not_exploited:"Source confirms absence of exploitation",confirmed_exploitation:"Exploitation confirmed"};
  return [status[state.exploitation], state.kev ? "CISA KEV" : null, state.ransomware ? "Ransomware" : null,
    state.vendor ? (es ? "Confirmación del fabricante" : "Vendor confirmation") : null,
    state.publicExploit ? (es ? "Exploit público" : "Public exploit") : null,
    state.cvss !== null ? "CVSS " + state.cvss.toFixed(1) : null,
    state.deadline ? (es ? "Plazo CISA: " : "CISA deadline: ") + timestamp(state.deadline, language) : null
  ].filter(Boolean).join(" · ");
}

export function CtiHistory({item, language}: {item: Vulnerability; language: Language}) {
  const cti = item.cti, es = language === "es";
  if (!cti) return null;
  const labels = (keys: string[]) => keys.map(key => CHANGE_LABELS[key]?.[es ? 0 : 1]).filter(Boolean).join(" · ");
  return <section className="cti-history" aria-label={es ? "Historial de inteligencia" : "Intelligence history"}>
    <h3>{cti.kind === "transition" ? (es ? "Cambio de estado" : "State transition") : (es ? "Primera observación" : "First observation")}</h3>
    <p>{es ? "Primera observación conservada: " : "First retained observation: "}{timestamp(cti.firstSeen, language)}.
      {" "}{es ? "Última observación: " : "Last observed: "}{timestamp(cti.lastSeen, language)}.</p>
    {cti.kind === "transition" ? <><strong>{labels(cti.changes)}</strong>
      <p>{cti.levelBefore ?? "—"} ({cti.priorityBefore?.toFixed(1) ?? "—"}) → {cti.levelAfter ?? "—"} ({cti.priorityAfter?.toFixed(1) ?? "—"})</p>
      <p><b>{es ? "Antes: " : "Before: "}</b>{stateSummary(cti.previous, language)}</p></> : null}
    <p><b>{es ? "Ahora: " : "Now: "}</b>{stateSummary(cti.current, language)}</p>
    {cti.current.action ? <p>{cti.current.action}</p> : null}
    {cti.history.length ? <details><summary>{es ? "Historial conservado" : "Retained history"} ({cti.historyCount})</summary>
      <ol>{cti.history.map((event, index) => <li key={String(event.at) + index}>
        <time>{timestamp(event.at, language)}</time><strong>{labels(event.changes)}</strong>
        <span>{event.before?.toFixed(1) ?? "—"} → {event.after?.toFixed(1) ?? "—"}</span>
        <span>{stateSummary(event.previous, language)} → {stateSummary(event.current, language)}</span>
        <span>{event.sources.map((source, i) => <a key={source.url + i} href={source.url} target="_blank" rel="noreferrer">{source.name} ↗ </a>)}</span>
      </li>)}</ol>
      {cti.historyCount > 8 ? <a href="https://github.com/JimBLogic/CyberDailyLog/blob/main/reports/cti-state.json" target="_blank" rel="noreferrer">{es ? "Ver historial completo" : "View full history"} ↗</a> : null}
    </details> : null}
  </section>;
}
