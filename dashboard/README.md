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
del contrato JSON. Consulta [docs/SELF_HOSTING.md](docs/SELF_HOSTING.md) para un
despliegue independiente.

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

## Estructura

- `app/`: páginas, UI y endpoints.
- `lib/`: normalización, recuperación y contrato de datos.
- `docs/`: operación, fuentes y compatibilidad.
- `tests/`: regresiones del render y API.
- `.openai/hosting.json`: identidad del proyecto de Sites; no impide ejecutarlo
  fuera de Sites.
