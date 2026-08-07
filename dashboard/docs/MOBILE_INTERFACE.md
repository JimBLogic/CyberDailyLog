# Compatibilidad móvil de la interfaz

Última revisión: 2026-08-07

## Cabecera y navegación

- El selector `EN / ES` permanece visible en todos los anchos. Antes se ocultaba por debajo de 680 px.
- Los botones de idioma y actualización tienen una zona táctil de aproximadamente 44 × 44 px.
- La navegación principal se desplaza horizontalmente en pantallas estrechas sin mover toda la página.
- La cabecera respeta las áreas seguras laterales de móviles con muesca o pantalla redondeada.
- El idioma activo se expone con `aria-pressed` y se conserva en el dispositivo cuando el almacenamiento del navegador está disponible.

## Respuesta de la interfaz

- Botones y enlaces usan `touch-action: manipulation` para reducir retrasos e interacciones táctiles accidentales.
- Los controles ofrecen respuesta visual al pulsarlos y el botón de actualización comunica su estado deshabilitado.
- Si el modo privado bloquea `localStorage`, el cambio de idioma y la lista de seguimiento continúan funcionando durante la sesión sin romper la interfaz.
- Los diálogos usan la altura dinámica del dispositivo para evitar quedar ocultos tras las barras del navegador móvil.

## Comprobaciones automatizadas

Las pruebas verifican que el selector no vuelva a ocultarse en móvil, que los controles táctiles conserven su tamaño mínimo, que el estado accesible del idioma se renderice y que la navegación mantenga el comportamiento de desplazamiento contenido.
