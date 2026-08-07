# Fuentes y estrategia de resiliencia

Última revisión: 2026-08-07

## Orden de recuperación

1. **Informe CyberDailyLog vía GitHub Raw.** Es la fuente principal porque conserva la normalización, correlación, priorización, salud de recopiladores y contexto editorial del proyecto.
2. **El mismo informe vía jsDelivr.** Es un respaldo de transporte y no una segunda fuente independiente. Evita que una incidencia puntual de `raw.githubusercontent.com` deje el panel vacío.
3. **Respaldo oficial NVD + CISA KEV.** Solo se activa si el informe principal no responde o supera 36 horas. NVD aporta CVE recientes y CISA aporta evidencia de explotación conocida. Este modo se etiqueta como degradado porque no incluye todo el contexto del pipeline.
4. **Copia verificada incluida.** Último recurso sin red. Siempre se presenta como histórico, nunca como inteligencia actual.

## APIs adoptadas

### NVD CVE API 2.0

- Proveedor: National Vulnerability Database, NIST.
- Endpoint: `https://services.nvd.nist.gov/rest/json/cves/2.0`
- Uso: una consulta de la ventana de publicación de 48 horas, únicamente en modo de respaldo.
- Control: caché de dos horas. Sin clave, NVD limita el acceso público a 5 peticiones por 30 segundos y recomienda automatizaciones mucho menos frecuentes que una consulta por visitante.
- Documentación: [NVD Vulnerability APIs](https://nvd.nist.gov/developers/vulnerabilities) y [NVD Start Here](https://nvd.nist.gov/developers/start-here).

### CISA Known Exploited Vulnerabilities

- Proveedor: Cybersecurity and Infrastructure Security Agency.
- Feed: `https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json`
- Uso: identificar CVE con explotación conocida, acciones exigidas y posible uso en ransomware. Si NVD falla, las entradas KEV más recientes todavía permiten un briefing de emergencia de alta señal.
- Documentación: [CISA KEV Catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog).

### FIRST EPSS

- Proveedor: FIRST EPSS Special Interest Group.
- Endpoint: `https://api.first.org/data/v1/epss`
- Uso: enriquecer como máximo 20 CVE ya seleccionados por el respaldo oficial. No se usa para sincronización masiva.
- Interpretación: probabilidad estimada de observar explotación en los próximos 30 días; no equivale a explotación confirmada ni sustituye CISA KEV.
- Atribución: FIRST solicita atribución cuando EPSS aparece en productos o publicaciones.
- Documentación: [FIRST EPSS data](https://www.first.org/epss/data) y [EPSS FAQ](https://www.first.org/epss/faq).

## Límites deliberados

- No se llama a NVD ni a FIRST durante el camino normal si el informe del repositorio está fresco.
- Un fallo de EPSS no bloquea NVD o CISA.
- Un feed vacío, una fecha inválida o una respuesta que no cumpla el esquema se trata como fallo; nunca se convierte en cero silencioso.
- La cadena completa utiliza límites de espera, coalescencia de peticiones en curso, caché y una última copia local.
- El modo de respaldo oficial no fabrica contexto de analistas, señales comunitarias ni histórico.

## Fuentes candidatas, no activadas

abuse.ch Feodo Tracker, abuse.ch URLhaus, Ransomware.live, AlienVault OTX, AbuseIPDB y C2IntelFeeds pueden aportar IOC y ransomware, pero requieren una revisión separada de términos, precisión, falsos positivos, privacidad, geolocalización, volumen y retención. No se incorporan solo porque aparezcan en otro proyecto.
