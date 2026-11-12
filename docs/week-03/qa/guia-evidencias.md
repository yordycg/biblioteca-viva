# Guía de evidencias — CP-15 a CP-21

> Para Gerald (QA). Esta guía no reemplaza los casos: indica cómo ejecutarlos y
> qué capturar. Los resultados se registran en `casos-prueba.md`; no se inventan.

## Preparación

```bash
just dashboard-demo      # datos ficticios del panel
just run                 # http://127.0.0.1:8000
```

Cuentas ficticias: `estudiante1@example.com`, `estudiante2@example.com`,
`bibliotecario1@example.com`, contraseña `demo1234`.

Capturas: 1280×800 y 360×800 cuando el caso sea visual. Nombres:
`docs/week-03/evidence/CP-XX-1280.png` y `CP-XX-360.png`.

## CP-15 — Fecha pasada

1. Como estudiante, abrir `/buscar/?vista=recursos`.
2. Elegir una fecha anterior a hoy y presionar **Filtrar**.
3. Capturar el borde rojo y el mensaje bajo el campo Fecha.
4. Repetir con la URL forzada de confirmación y verificar que no crea reserva.

## CP-16 — Inventario en el panel

1. Como bibliotecario, abrir `/bibliotecario/`.
2. Capturar las tarjetas de inventario y la línea de tiempo.
3. Comparar los contadores con las reservas del día.

## CP-17 — Ventana de reserva

1. Revisar que el selector muestre 13 bloques de 09:00 a 22:00.
2. Con la hora actual, verificar que no aparezcan bloques iniciados ni con menos
   de 15 minutos de antelación. Si hace falta, usar
   `DEMO_MODE=1 DEMO_NOW=...` en una terminal aparte.
3. Forzar un bloque no disponible y capturar el rechazo.

## CP-18 — Catálogo, ficha y préstamo

1. Como estudiante, abrir la pestaña **Libros**.
2. Filtrar por autor, abrir una ficha y capturar carátula/datos.
3. Solicitar 7 días, confirmar y capturar el QR y “Mis reservas” con la fecha de
   devolución.

## CP-19 — Solapamiento y límite

1. Crear dos préstamos activos con libros distintos.
2. Intentar un tercero y capturar el rechazo.
3. Intentar un rango solapado del mismo libro y capturar el rechazo.

## CP-20 — Catálogo inicial y “Solo disponibles”

1. Abrir `/buscar/?vista=recursos` sin filtros.
2. Capturar todos los recursos con su estado (incluido un ocupado).
3. Activar “Solo disponibles” y verificar que el ocupado desaparece.
4. Confirmar que no hay errores antes de presionar Filtrar.

## CP-21 — Panel operativo

1. Como bibliotecario, revisar KPIs, agenda, ocupación, sanciones y filtros.
2. Capturar 1280 y 360.
3. Verificar que la barra superior no muestre el rol.
4. Probar los filtros por estado y por código.

## Cierre

- Actualizar `casos-prueba.md`, `matriz-trazabilidad.md` y `defectos.md`.
- Cada defecto: `DEF-XX`, severidad, pasos, responsable y re-prueba.
- Nada pasa a “Aprobado” sin captura o log real.
