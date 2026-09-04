# Auditoría de privacidad y almacenamiento · CyberDailyLog Sites

Revisión del código fuente y del artefacto de producción preparada el **4 de
septiembre de 2026**. Alcance: rutas, almacenamiento del navegador, cookies,
red, recursos externos, APIs, formularios, autenticación, IndexedDB, service
workers y capacidades de Sites.

## Inventario antes del cambio

| Superficie | Inventario exacto |
| --- | --- |
| Cookies de la aplicación | Ninguna lectura o escritura de `document.cookie`; ninguna cabecera `Set-Cookie` creada por CyberDailyLog. Las cookies o registros del proveedor no forman parte del código de la aplicación. |
| `localStorage` | `cyberdailylog-language` (`es` o `en`) y `cyberdailylog-watchlist` (lista JSON de identificadores públicos). Lectura al montar la interfaz; escritura al pulsar el selector de idioma o añadir/quitar un aviso. |
| `sessionStorage` / IndexedDB | El código de CyberDailyLog no usaba ninguno. La build de Vinext incluía `__vinext_rsc_initial_reload__` en `sessionStorage` como guarda técnica temporal contra bucles de recarga; IndexedDB no aparecía. |
| Service workers | Sin registro ni fichero de service worker de la aplicación. |
| Autenticación | Sitio público sin login. Existía un helper de plantilla `app/chatgpt-auth.ts`, no importado ni desplegado como función activa. |
| Bases de datos y archivos | `.openai/hosting.json` declaraba `d1: null` y `r2: null`. Los ejemplos D1 del repositorio no estaban importados ni vinculados al Site. |
| Formularios | Ninguno. |
| APIs propias | `GET /api/intelligence`, `GET /api/export` y `GET /api/source-media`. Las dos primeras devolvían datos públicos. La tercera obtenía imágenes de artículos permitidos y las servía mediante el mismo origen. |
| Red del navegador | HTML, JavaScript, CSS y fuentes locales; consulta al mismo origen `/api/intelligence`; descargas del mismo origen; enlaces externos solo al pulsarlos. Las tarjetas solicitaban automáticamente `/api/source-media`, que podía provocar una consulta servidor-a-servidor a SANS, Krebs o GitHub. El runtime Vinext realiza navegación RSC al mismo origen con credenciales del origen, por lo que puede transportar cookies técnicas del proveedor; no transporta el contenido de `localStorage`. |
| Red del servidor | Datos esenciales desde `raw.githubusercontent.com`, `cdn.jsdelivr.net`, `services.nvd.nist.gov`, `www.cisa.gov` y `api.first.org`; imágenes no esenciales desde hosts permitidos por `/api/source-media`. No se añadían preferencias, cookies o identificadores del visitante a esas peticiones. |
| Recursos de terceros | Sin scripts de analítica, anuncios, píxeles, iframes, embeds ni fuentes remotas. Las imágenes editoriales podían provenir de terceros a través del proxy del Site. |
| Métricas del proveedor | Sites registra automáticamente recuentos de visitantes únicos y páginas vistas al margen del SDK de la aplicación. La configuración pública del proyecto, el manifiesto y las herramientas documentadas no exponen un interruptor para desactivarlo. |
| Logs de hosting | El proveedor puede tratar IP, navegador, fecha/hora e interacción técnica para prestar, mantener, medir y proteger el servicio conforme a sus políticas. |

## Inventario después del cambio

| Superficie | Estado resultante |
| --- | --- |
| Cookies de la aplicación | Siguen siendo cero. Las pruebas rechazan acceso a `document.cookie` y comprueban que las respuestas de la aplicación no añaden `Set-Cookie`. |
| `localStorage` | Solo los dos nombres documentados. Un helper único valida idioma, formato, longitud y cantidad de elementos. La escritura sigue ocurriendo únicamente tras pulsar idioma o seguimiento. |
| Borrado local | “Borrar preferencias locales” está disponible en el footer de todas las vistas y en `/privacidad`; elimina ambas claves y nada más. |
| `sessionStorage` / IndexedDB / service workers | El código propio sigue sin usar `sessionStorage`, IndexedDB o service workers. La build conserva únicamente la guarda técnica de Vinext `__vinext_rsc_initial_reload__`, limitada a la sesión de la pestaña; los tests fallan ante otra clave o API no prevista. |
| Autenticación, formularios, D1 y R2 | Sin autenticación ni formularios activos; se retiró el helper de autenticación no usado; D1 y R2 siguen en `null`. |
| APIs | Se conservan `/api/intelligence` y `/api/export`. Se retira `/api/source-media` y las imágenes remotas automáticas se sustituyen por la composición gráfica local ya existente. |
| Red del navegador | Solo mismo origen para recursos y API. La actualización propia de `/api/intelligence` usa `credentials: 'omit'` y `referrerPolicy: 'no-referrer'`; la navegación interna de Vinext sigue pudiendo incluir credenciales técnicas del mismo origen. La CSP fija `connect-src 'self'`, `img-src 'self' data:`, `frame-src 'none'`, `object-src 'none'`, `form-action 'none'` y `worker-src 'none'`. |
| Red del servidor | Una política de ejecución limita las peticiones esenciales a los cinco hosts de datos documentados y exige HTTPS. Añadir otro host requiere modificar explícitamente la lista y hace visible el cambio en revisión. |
| Seguimiento y publicidad | No se añaden SDK, analítica propia, anuncios, fingerprinting, píxeles, embeds ni iframes. |
| Métricas y logs de Sites | No cambian: son una capa automática del proveedor que esta aplicación no puede bloquear ni presentar honestamente como opcional. |
| Transparencia | `/privacidad` ofrece texto ES/EN, contacto, duración y borrado de preferencias, fuentes, limitación de Sites, logs técnicos, derechos y enlaces oficiales. |

## Hosts aprobados

### Peticiones esenciales del servidor

- `raw.githubusercontent.com` — informe principal del repositorio.
- `cdn.jsdelivr.net` — transporte alternativo del mismo informe.
- `services.nvd.nist.gov` — respaldo oficial NVD.
- `www.cisa.gov` — catálogo CISA KEV.
- `api.first.org` — enriquecimiento EPSS.

Estas llamadas se originan en el servidor de Sites. No contienen
`cyberdailylog-language`, `cyberdailylog-watchlist` ni un identificador creado
por CyberDailyLog.

### Navegación iniciada por el visitante

Los demás hosts literales aprobados pertenecen a fuentes, avisos, documentación,
GitHub u OpenAI. Se abren únicamente al pulsar un enlace; no se usan como scripts,
estilos, fuentes, iframes o imágenes automáticas.

## Ajuste de Analytics de Sites

No se ha encontrado un control documentado para desactivar las métricas
automáticas de Sites en este proyecto. La comprobación cubrió:

1. `.openai/hosting.json` (solo identidad, D1 y R2 en este proyecto);
2. las operaciones publicadas de Sites (acceso, metadatos, dominio, variables,
   versiones y despliegue; ninguna operación de Analytics);
3. la guía pública **Creating and managing ChatGPT Sites**, que documenta
   creación, edición, publicación, acceso, autenticación y datos/logs, pero no un
   interruptor de Analytics.

Por tanto no se implementa un banner con “Rechazar” ni un panel de consentimiento:
no hay tecnología no esencial controlable por la aplicación que bloquear y no
existe una API con la que el botón pudiera rechazar la medición del proveedor.

Referencias del proveedor:

- [Creating and managing ChatGPT Sites](https://help.openai.com/en/articles/20001339-creating-and-managing-chatgpt-sites)
- [Política de privacidad de OpenAI para Europa](https://openai.com/policies/eu-privacy-policy/)
- [Política de cookies de OpenAI](https://openai.com/policies/cookie-policy/)
- [Portal de privacidad de OpenAI](https://privacy.openai.com/)

## Controles de regresión

`npm test` construye el artefacto y falla si aparece cualquiera de estas clases:

- Google Analytics/gtag, Meta Pixel, Hotjar o Microsoft Clarity;
- publicidad o hosts de publicidad conocidos;
- APIs habituales de fingerprinting;
- cookies de aplicación, IndexedDB, service workers, formularios, iframes,
  embeds u objetos;
- una tercera preferencia persistente o una segunda clave de sesión en la build;
- un host externo literal no aprobado;
- una llamada de servidor que eluda la política de cinco hosts esenciales;
- una ruta sin el aviso de privacidad, las cabeceras de seguridad o las garantías
  de almacenamiento comprobadas.
