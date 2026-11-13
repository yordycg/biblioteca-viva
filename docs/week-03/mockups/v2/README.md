# Mockups v2 — UI implementada

> Capturas reales de la aplicación Django al cierre de la corrección S3. No son
> renders de Stitch: son evidencia de la interfaz implementada.

## Relación con Stitch v1

- **v1:** proyecto de Google Stitch (SEM3-T1, Vicente Díaz). En Drive solo queda
  el `.zip` `mockups/stitch_bibliotecaviva_ui_redesign.zip`; no es editable y no
  se versiona porque depende de Tailwind CDN y fotos remotas.
- **v2:** implementación real en `reservas/templates/` y
  `reservas/static/reservas/styles.css`. Es la fuente de verdad visual.
- La evolución v1 → v2 responde a la revisión docente: login limpio, pestañas de
  búsqueda, catálogo de libros, ficha de una card, 13 bloques y panel operativo.

## Capturas

| Pantalla | 1280 px | 360 px |
|---|---|---|
| Login sin credenciales demo | `login-1280.png` | `login-360.png` |
| Búsqueda · Libros (filtros vacíos) | `buscar-libros-1280.png` | `buscar-libros-360.png` |
| Búsqueda · Salas y equipos (filtros vacíos) | `buscar-recursos-1280.png` | `buscar-recursos-360.png` |
| Error de validación al enviar sin filtros | `error-libros-1280.png` | `error-libros-360.png` |
| Ficha de libro en una card | `ficha-1280.png` | `ficha-360.png` |
| Panel · Operación | `panel-1280.png` | `panel-360.png` |
| Panel · Inventario filtrado por “Sala” | `panel-inventario-1280.png` | `panel-inventario-360.png` |
| Panel · Reservas del día con acciones | `panel-reservas-1280.png` | `panel-reservas-360.png` |
| Panel · Validación | `panel-validacion-1280.png` | `panel-validacion-360.png` |

Tamaños: 1280×1200 y 360×1400. Se generaron con Chromium headless contra el
servidor local, con la sesión de los usuarios ficticios del seed y la ventana
fijada en cada resolución.

## Nota para el informe

Los mockups v1 se mantienen como referencia histórica del rediseño. Para evaluar
la entrega se usan estas capturas v2 y `docs/week-03/design/design-system.md`.
