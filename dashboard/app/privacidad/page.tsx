import Link from "next/link";
import { ClearLocalPreferencesButton } from "./ClearLocalPreferencesButton";

const OPENAI_SITES_GUIDE =
  "https://help.openai.com/en/articles/20001339-creating-and-managing-chatgpt-sites";
const OPENAI_PRIVACY_POLICY = "https://openai.com/policies/eu-privacy-policy/";
const OPENAI_COOKIE_POLICY = "https://openai.com/policies/cookie-policy/";
const OPENAI_PRIVACY_PORTAL = "https://privacy.openai.com/";

export default function PrivacyPage() {
  return (
    <main className="privacy-shell">
      <header className="privacy-header">
        <Link href="/" aria-label="Volver a CyberDailyLog">
          ← CyberDailyLog
        </Link>
        <span>Última revisión · 4 septiembre 2026</span>
      </header>

      <section className="privacy-intro" lang="es">
        <span className="eyebrow">Privacidad por diseño</span>
        <h1>Privacidad y almacenamiento local</h1>
        <p>
          No añadimos analítica publicitaria, publicidad ni tecnologías de
          seguimiento. ChatGPT Sites, como proveedor de alojamiento, puede
          tratar datos técnicos necesarios para prestar, medir y proteger el
          servicio. Esta página separa con claridad ambas capas.
        </p>
      </section>

      <div className="privacy-grid">
        <article className="privacy-language" lang="es">
          <h2>Información en español</h2>

          <section>
            <h3>Responsable editorial y contacto</h3>
            <p>
              CyberDailyLog está editado por <strong>Jaime Ramsden de Frutos</strong>.
              Para consultas de privacidad relacionadas con el contenido o las
              funciones de esta web: <a href="mailto:jrf91@pm.me">jrf91@pm.me</a>.
            </p>
          </section>

          <section>
            <h3>Preferencias guardadas en este dispositivo</h3>
            <ul>
              <li>
                <code>cyberdailylog-language</code>: guarda únicamente
                <code> es </code> o <code> en </code> cuando eliges un idioma.
              </li>
              <li>
                <code>cyberdailylog-watchlist</code>: guarda solo los identificadores
                públicos de los avisos que añades a seguimiento.
              </li>
            </ul>
            <p>
              Ambas preferencias permanecen en <code>localStorage</code> hasta que
              las borres con el control inferior o desde la configuración del
              navegador. El código no las envía a CyberDailyLog, a las APIs de
              fuentes ni a un servidor propio, y no añade un identificador del
              visitante.
            </p>
            <p>
              El runtime Vinext generado durante la build usa además
              <code> __vinext_rsc_initial_reload__ </code> en
              <code> sessionStorage</code> como salvaguarda técnica frente a un
              bucle de recarga. Dura solo durante la sesión de la pestaña, no es
              una preferencia, no identifica al visitante y CyberDailyLog no la
              envía a sus APIs.
            </p>
          </section>

          <section>
            <h3>Métricas automáticas de Sites</h3>
            <p>
              ChatGPT Sites registra automáticamente recuentos de visitantes únicos
              y páginas vistas aunque esta aplicación no instale un SDK de
              analítica. CyberDailyLog no añade esa medición ni recibe en su código
              una copia individualizada de sus datos.
            </p>
            <p>
              A fecha de esta revisión no existe en la configuración documentada de
              este proyecto, en su manifiesto ni en las herramientas publicadas de
              Sites un ajuste para desactivar esa medición. Es una limitación del
              proveedor: no se presenta como opcional y ningún botón de esta web
              promete rechazarla.
            </p>
          </section>

          <section>
            <h3>Hosting, fuentes y finalidad</h3>
            <p>
              OpenAI y sus proveedores de infraestructura pueden tratar registros
              técnicos —por ejemplo, dirección IP, navegador, fecha y hora de la
              solicitud e interacción con el servicio— para prestar, mantener,
              medir, depurar y proteger Sites. Consulta la documentación y las
              políticas del proveedor enlazadas más abajo.
            </p>
            <p>
              Las navegaciones internas del runtime se solicitan al mismo origen de
              Sites y pueden incluir cookies técnicas establecidas por el proveedor.
              CyberDailyLog no crea, lee ni modifica esas cookies.
            </p>
            <p>
              El servidor de CyberDailyLog consulta datos públicos esenciales de
              GitHub Raw, jsDelivr, NVD, CISA y FIRST. Esas peticiones salen desde el
              servidor de Sites y no incluyen las preferencias locales ni un
              identificador creado por CyberDailyLog. Los enlaces a otras fuentes
              solo se abren cuando decides pulsarlos.
            </p>
          </section>

          <section>
            <h3>Formularios, cuentas y tecnologías no esenciales</h3>
            <p>
              La aplicación no incluye formularios, cuentas, autenticación,
              publicidad, píxeles, fingerprinting, embeds, iframes, IndexedDB ni
              service workers. No se ha encontrado tecnología no esencial
              controlable por la aplicación que deba bloquearse antes de una
              elección; por eso no se muestra un banner o panel de consentimiento
              ficticio.
            </p>
          </section>

          <section>
            <h3>Derechos</h3>
            <p>
              Puedes solicitar información, acceso, rectificación, supresión,
              limitación u oposición cuando proceda escribiendo al contacto
              editorial. Para el tratamiento realizado por OpenAI como proveedor,
              utiliza su Portal de Privacidad y consulta su política aplicable.
            </p>
          </section>
        </article>

        <article className="privacy-language" lang="en">
          <h2>Information in English</h2>

          <section>
            <h3>Publisher and contact</h3>
            <p>
              CyberDailyLog is published by <strong>Jaime Ramsden de Frutos</strong>.
              For privacy questions about this website&apos;s content or features,
              contact <a href="mailto:jrf91@pm.me">jrf91@pm.me</a>.
            </p>
          </section>

          <section>
            <h3>Preferences stored on this device</h3>
            <ul>
              <li>
                <code>cyberdailylog-language</code> stores only <code>es</code> or
                <code> en</code> after you choose a language.
              </li>
              <li>
                <code>cyberdailylog-watchlist</code> stores only the public IDs of
                advisories you add to your watchlist.
              </li>
            </ul>
            <p>
              Both stay in <code>localStorage</code> until you use the control below
              or clear this site&apos;s browser data. The application does not send
              them to CyberDailyLog, source APIs or an app-owned server, and it does
              not add a visitor identifier.
            </p>
            <p>
              The Vinext runtime generated during the build also uses
              <code> __vinext_rsc_initial_reload__ </code> in
              <code> sessionStorage</code> as a technical reload-loop safeguard. It
              lasts only for the tab session, is not a preference, does not identify
              the visitor, and CyberDailyLog does not send it to its APIs.
            </p>
          </section>

          <section>
            <h3>Automatic Sites metrics</h3>
            <p>
              ChatGPT Sites automatically records unique-visitor and page-view
              counts even when this application installs no analytics SDK.
              CyberDailyLog does not add that measurement and its code receives no
              visitor-level copy of those metrics.
            </p>
            <p>
              At the review date, this project&apos;s documented settings, manifest
              and published Sites tools expose no switch to disable that
              measurement. This is a provider limitation, not an optional feature,
              and no control on this website claims to reject it.
            </p>
          </section>

          <section>
            <h3>Hosting, data sources and purpose</h3>
            <p>
              OpenAI and its infrastructure providers may process technical logs,
              such as IP address, browser, request date and time, and service
              interaction, to provide, maintain, measure, debug and protect Sites.
            </p>
            <p>
              Internal runtime navigation requests stay on the Sites origin and may
              include technical cookies set by the provider. CyberDailyLog does not
              create, read or modify those cookies.
            </p>
            <p>
              The CyberDailyLog server fetches essential public data from GitHub
              Raw, jsDelivr, NVD, CISA and FIRST. Those requests originate from the
              Sites server and contain neither local preferences nor a CyberDailyLog
              visitor identifier. Other source links open only when you choose them.
            </p>
          </section>

          <section>
            <h3>Forms, accounts and non-essential technology</h3>
            <p>
              The application has no forms, accounts, authentication, advertising,
              pixels, fingerprinting, embeds, iframes, IndexedDB or service workers.
              The audit found no app-controlled non-essential technology that must
              be blocked before a choice, so no misleading consent banner or panel
              is shown.
            </p>
          </section>

          <section>
            <h3>Your rights</h3>
            <p>
              You may request information, access, correction, deletion,
              restriction or objection where applicable by contacting the
              publisher. For processing carried out by OpenAI as provider, use its
              Privacy Portal and consult the applicable policy.
            </p>
          </section>
        </article>
      </div>

      <ClearLocalPreferencesButton />

      <nav className="privacy-provider-links" aria-label="Políticas del proveedor">
        <a href={OPENAI_SITES_GUIDE} target="_blank" rel="noreferrer">
          Guía oficial de ChatGPT Sites
        </a>
        <a href={OPENAI_PRIVACY_POLICY} target="_blank" rel="noreferrer">
          Política de privacidad de OpenAI (Europa)
        </a>
        <a href={OPENAI_COOKIE_POLICY} target="_blank" rel="noreferrer">
          Política de cookies de OpenAI
        </a>
        <a href={OPENAI_PRIVACY_PORTAL} target="_blank" rel="noreferrer">
          Portal de privacidad de OpenAI
        </a>
      </nav>
    </main>
  );
}
