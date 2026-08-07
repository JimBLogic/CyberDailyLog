# Inspiración y atribución

Última revisión: 2026-08-07

CyberDailyLog revisó [World Monitor](https://github.com/koala73/worldmonitor) como referencia de producto y arquitectura para comunicar mejor la procedencia, la frescura y los huecos de cobertura.

## Ideas adoptadas

- Mostrar frescura `reciente / envejeciendo / desactualizada / crítica` según la cadencia esperada de cada fuente, y no confundir una ejecución histórica correcta con datos actuales.
- Declarar huecos de inteligencia cuando una fuente está retrasada, degradada, caída o solo aporta datos de prueba.
- Mantener evidencia, contexto experto y conversación comunitaria en carriles de confianza separados.
- Diseñar una cadena de recuperación explícita, con caché, timeouts y estado visible.
- Separar fuentes principales de fuentes opcionales y expresar la cobertura como suficiente, limitada o insuficiente.
- Evitar fallos en cascada: las rutas que fallan entran en una pausa temporal con reintento visible, y los complementos se resuelven de forma independiente.

La implementación es propia de CyberDailyLog. No se ha copiado código, estilos, respuestas, salidas, SDK ni paquetes de World Monitor, y tampoco se consume su REST API o MCP alojado.

## Licencia

El código de World Monitor se publica bajo `AGPL-3.0-only`; su servicio alojado y sus salidas tienen condiciones específicas por plan. Por eso se usa únicamente como inspiración arquitectónica. Cualquier integración futura exigiría documentar el componente exacto, licencia, términos de API/salidas, credenciales, retención y atribución.

Las fuentes operativas incorporadas en este cambio se consultan directamente a sus proveedores originales y se documentan en [docs/SOURCE_RESILIENCE.md](docs/SOURCE_RESILIENCE.md).

## Criterio aplicado a APIs vistas en World Monitor

No toda integración útil en otro producto es adecuada como respaldo anónimo. En
la revisión del 7 de agosto de 2026:

- **URLhaus** no se activó porque la descarga de datasets comunitarios exige
  Auth-Key y está sujeta a límites y condiciones de uso propios.
- **Feodo Tracker** no se activó porque el proveedor indica que el dataset está
  vacío tras Operation Endgame; un feed vacío no debe aparentar “cero amenazas”.
- **AlienVault OTX y AbuseIPDB** siguen como candidatos con credenciales; antes
  de usarlos habría que definir presupuesto, privacidad, retención, cuota y qué
  decisión defensiva cambia cada dato.

La mejora implementada fortalece las fuentes oficiales ya verificadas (NVD,
CISA y FIRST) y hace visibles sus límites, en lugar de aumentar el número de
logos o llamadas externas.
