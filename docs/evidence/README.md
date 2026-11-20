# Evidencias — Semana 3

## RNF-02 · Interfaz responsiva (360 px y 1280 px)

Carpeta `rnf-02/`. Capturas de las seis pantallas del MVP en dos resoluciones:

| Pantalla | 360×900 | 1280×900 |
|---|---|---|
| Login | `rnf-02-login-360.png` | `rnf-02-login-1280.png` |
| Búsqueda | `rnf-02-buscar-360.png` | `rnf-02-buscar-1280.png` |
| Confirmar reserva | `rnf-02-confirmar-360.png` | `rnf-02-confirmar-1280.png` |
| Comprobante QR | `rnf-02-qr-360.png` | `rnf-02-qr-1280.png` |
| Mis reservas | `rnf-02-mis-reservas-360.png` | `rnf-02-mis-reservas-1280.png` |
| Panel bibliotecario | `rnf-02-bibliotecario-360.png` | `rnf-02-bibliotecario-1280.png` |

**Cómo se generaron (2026-11-13).** Sobre la base cargada con
`python manage.py seed --reset` y con el servidor local en marcha:

1. Chromium headless (Playwright) abrió la aplicación real y se autenticó con los
   usuarios ficticios del seed (`estudiante1@example.com`,
   `estudiante2@example.com`, `bibliotecario1@example.com`).
2. Cada pantalla se capturó con la ventana fijada en 360×900 y 1280×900, sin
   modificar templates, datos ni estilos. Las animaciones se desactivan con
   `prefers-reduced-motion`.
3. Las capturas de `../mockups/v2/` usan el mismo procedimiento con ventanas de
   360×1400 y 1280×1200.

Si la base está vacía o con datos de prueba, las pantallas se ven distintas: para
reproducirlas hay que ejecutar `python manage.py seed --reset` antes.

**Qué acredita.** Que las seis pantallas renderizan sin desbordes ni solapamientos
a 360, 768 y 1280 px, con la barra superior, los filtros, las tarjetas y la tabla
del día adaptándose según el sistema de diseño. Estas capturas son la evidencia de
CP-09 (RNF-02).

**Qué no acredita.** Lighthouse no se ejecutó porque la pauta no lo solicita; la
accesibilidad se documenta con la revisión visual en las tres resoluciones.

## Casos ejecutados (2026-11-13 a 2026-11-17)

26 de los 26 casos ejecutados sobre el flujo real: 25 aprobados y CP-26 fallido
(DEF-03, sin JavaScript «Salas y equipos» no se puede filtrar). Cada uno se
registra en `../qa/casos-prueba.md` con su resultado y la ruta de su evidencia.
CP-01 a CP-06 se re-ejecutaron el 2026-11-14 en el navegador; CP-07 y CP-11 a
CP-14 se ejecutaron el 2026-11-13 con el script local; CP-26 se ejecutó el
2026-11-19 en Chromium con y sin JavaScript.

| Caso | Evidencia | Qué muestra |
|---|---|---|
| CP-01 | `CP-01.png` | Recursos del bloque con su estado; «Solo disponibles» oculta los ocupados |
| CP-02 | `CP-02.png` | Reserva creada y su QR |
| CP-03 | `CP-03.png` | Tercera reserva del día rechazada |
| CP-04 | `CP-04.png` | QR inexistente y segundo uso rechazados |
| CP-05 | `CP-05.png` | Devolución dentro del bloque, sin sanción |
| CP-06 | `CP-06.png` | Devolución tardía con sanción de 7 días |
| CP-07 | `CP-07.png` | Credenciales inválidas rechazadas |
| CP-11 | `CP-11.png` | Búsqueda sin resultados |
| CP-12 | `CP-12.png` | Devolución en la hora límite, sin sanción |
| CP-13 | `CP-13.png` | “Mis reservas” con el QR reabrible |
| CP-14 | `CP-14.png` | QR de una reserva ajena rechazado |
| CP-10 | `CP-10.png` | Ejecutado y aprobado el 2026-11-17 |
| CP-15 | `CP-15.png` | Ejecutado y aprobado el 2026-11-17 |
| CP-16 | `CP-16.png` | Ejecutado y aprobado el 2026-11-17 |
| CP-17 | `CP-17.png` | Ejecutado y aprobado el 2026-11-17 |
| CP-18 | `CP-18.png` | Ejecutado y aprobado el 2026-11-17 |
| CP-19 | `CP-19.png` | Ejecutado y aprobado el 2026-11-17 |
| CP-20 | `CP-20.png` | Ejecutado y aprobado el 2026-11-17 |
| CP-21 | `CP-21.png` | Ejecutado y aprobado el 2026-11-17 |
| CP-22 | `CP-22.png` | Ejecutado y aprobado el 2026-11-17 |
| CP-23 | `CP-23.png` | Ejecutado y aprobado el 2026-11-17 |
| CP-24 | `CP-24.png` | Ejecutado y aprobado el 2026-11-17 |
| CP-25 | `CP-25.png` | Ejecutado y aprobado el 2026-11-17 |
| CP-26 | `CP-26.png` | Filtros reactivos con y sin JavaScript: falla el paso 5 (DEF-03) |
| CP-08 | `CP-08.txt` | 20 peticiones de reserva + QR: 27 ms de promedio (RNF-01) |
| CP-09 | `rnf-02/` | Seis pantallas a 360 y 1280 px y tres a 768 px (RNF-02) |

**Cómo se generaron.** CP-07 y CP-11 a CP-14 con `local/tools/ejecutar_cp.py`,
que reinicia el seed, recorre el flujo con el cliente de Django y captura la
pantalla resultante con Chromium a 1280×900. CP-01 a CP-06 se re-ejecutaron el
2026-11-14 en el navegador (Chromium) sobre la aplicación; la hora se fijó con
`DEMO_MODE`/`DEMO_NOW` para los casos de devolución. Las capturas de CP-01 a CP-06
se recortaron y rotularon por escenario (A/B); los rótulos son anotaciones y no
forman parte de la interfaz. CP-26 se ejecutó el 2026-11-19 con Chromium
(Playwright) sobre el flujo real, activando y desactivando JavaScript por
contexto de navegador. DEF-01 y DEF-02 son correcciones de los casos CP-01 y
CP-23; **DEF-03 es el único defecto de producto** y se registra en
`../qa/defectos.md`.
