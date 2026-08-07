# Inspiración y atribución

Última revisión: 2026-08-07

CyberDailyLog revisó [World Monitor](https://github.com/koala73/worldmonitor) como referencia de producto y arquitectura para comunicar mejor la procedencia, la frescura y los huecos de cobertura.

## Ideas adoptadas

- Mostrar la frescura por fuente y no confundir una ejecución histórica correcta con datos actuales.
- Declarar huecos de inteligencia cuando una fuente está retrasada, degradada, caída o solo aporta datos de prueba.
- Mantener evidencia, contexto experto y conversación comunitaria en carriles de confianza separados.
- Diseñar una cadena de recuperación explícita, con caché, timeouts y estado visible.

La implementación es propia de CyberDailyLog. No se ha copiado código, estilos, respuestas, salidas, SDK ni paquetes de World Monitor, y tampoco se consume su REST API o MCP alojado.

## Licencia

El código de World Monitor se publica bajo `AGPL-3.0-only`; su servicio alojado y sus salidas tienen condiciones específicas por plan. Por eso se usa únicamente como inspiración arquitectónica. Cualquier integración futura exigiría documentar el componente exacto, licencia, términos de API/salidas, credenciales, retención y atribución.

Las fuentes operativas incorporadas en este cambio se consultan directamente a sus proveedores originales y se documentan en [docs/SOURCE_RESILIENCE.md](docs/SOURCE_RESILIENCE.md).
