# CyberDailyLog Dashboard

Panel bilingüe y autónomo para convertir las salidas públicas de
[CyberDailyLog](https://github.com/JimBLogic/CyberDailyLog) en un briefing diario
comprensible. La misma base de código se publica en OpenAI Sites y se guarda en
`dashboard/` del repositorio para poder ejecutarla sin Sites.

## Qué ofrece

- priorización de CVE, señales de explotación y acciones defensivas;
- evidencia, contexto experto y conversación comunitaria en carriles separados;
- GitHub Raw → jsDelivr → NVD/CISA/FIRST → copia incluida como cadena de respaldo;
- frescura por cadencia, confianza de cobertura y fallos visibles;
- interfaz en español e inglés, responsive y usable con teclado o tacto;
- API JSON en `/api/intelligence` y exportaciones en `/api/export`.
- privacidad explicada en `/privacidad`, con solo idioma y seguimiento en el
  dispositivo y un control para borrarlos.

## Ejecutar en local

Requiere Node.js `>=22.13.0` y npm. Desde el repositorio principal:

```bash
cd dashboard
npm ci
npm run dev
```

Abre la dirección que muestre Vite, normalmente `http://localhost:5173`. La
configuración predeterminada no requiere claves ni archivo `.env`.

Para comprobar el mismo artefacto que se despliega:

```bash
npm test
npm start
```

`npm test` construye y valida el Worker antes de ejecutar las pruebas del HTML y
del contrato JSON, la política de red y las regresiones de privacidad. Consulta
[docs/PRIVACY_AUDIT.md](docs/PRIVACY_AUDIT.md) para el inventario antes/después y
[docs/SELF_HOSTING.md](docs/SELF_HOSTING.md) para un despliegue independiente.

## Espejo GitHub ↔ Sites

`dashboard/` de `JimBLogic/CyberDailyLog` es la copia reproducible de esta fuente.
Antes de publicar, compara ambas copias desde cualquiera de ellas:

```bash
npm run verify:mirror -- /ruta/a/la/otra/copia
```

La comprobación compara rutas y SHA-256. Solo ignora dependencias, builds y cachés,
además de `.env.example`, `next-env.d.ts` y `next.config.mjs`, que se conservan como
compatibilidad exclusiva del repositorio principal.

## Datos y resiliencia

El camino normal lee los informes generados por el pipeline Python del
repositorio. Las APIs oficiales solo se consultan cuando el informe principal no
está disponible o está retrasado. Los límites, cadencias y candidatos descartados
se documentan en [docs/SOURCE_RESILIENCE.md](docs/SOURCE_RESILIENCE.md).

La revisión de World Monitor y su tratamiento de licencia están en
[INSPIRATION.md](INSPIRATION.md). No se ha copiado código AGPL ni se consume la
API alojada de ese proyecto.

## Scripts útiles

- `npm run dev`: desarrollo local.
- `npm run build`: artefacto de producción verificado.
- `npm start`: servidor local a partir del artefacto.
- `npm test`: build, contrato y regresiones de interfaz.
- `npm run lint`: análisis estático.
- `npm run verify:mirror -- <ruta>`: paridad exacta entre Sites y `dashboard/`.

## Estructura

- `app/`: páginas, UI y endpoints.
- `lib/`: normalización, recuperación y contrato de datos.
- `docs/`: operación, fuentes y compatibilidad.
- `tests/`: regresiones del render y API.
- `.openai/hosting.json`: identidad del proyecto de Sites; no impide ejecutarlo
  fuera de Sites.
