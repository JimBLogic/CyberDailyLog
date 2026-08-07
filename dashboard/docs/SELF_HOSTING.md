# Ejecución y alojamiento independiente

Última revisión: 2026-08-07

El directorio `dashboard/` del repositorio contiene exactamente la aplicación
publicada en Sites. No depende de una base de datos de Sites, de autenticación de
ChatGPT ni de secretos para funcionar.

## Desarrollo local

```bash
git clone https://github.com/JimBLogic/CyberDailyLog.git
cd CyberDailyLog/dashboard
npm ci
npm run dev
```

Requisito: Node.js `>=22.13.0`. La UI obtiene datos públicos del propio
repositorio y conserva una copia verificada para trabajar sin red.

## Ensayo de producción

```bash
npm test
npm start
```

El primer comando ejecuta el build, valida el manifiesto desplegable y comprueba
el HTML, el selector de idioma, las fechas y el contrato de `/api/intelligence`.
El segundo arranca el artefacto de Vinext. Sitúa delante el proxy HTTPS habitual
de tu proveedor si se expone a Internet.

## Alojamiento en otra plataforma

Usa un servicio Linux con Node.js 22 o superior y configura:

1. directorio de trabajo: `dashboard`;
2. instalación: `npm ci`;
3. build: `npm run build`;
4. inicio: `npm start`;
5. comprobación de salud: petición HTTP a `/api/intelligence` y respuesta `200`.

No guardes tokens en el repositorio. Si en el futuro se habilita una fuente con
credenciales, debe ser opcional, configurarse mediante secretos del proveedor y
degradarse sin bloquear NVD, CISA, FIRST ni la copia local.

## Paridad Sites ↔ GitHub

La fuente de verdad del panel es `dashboard/` en GitHub. Cada actualización de
Sites se copia completa a ese directorio y se valida de nuevo antes del merge.
Los informes consumidos siguen viviendo en `reports/`; por eso una clonación del
repositorio conserva tanto el generador como la interfaz.
