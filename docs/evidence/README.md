# Evidencias

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

**Cómo se generaron (2026-11-13; regeneradas el 2026-11-20 tras DEF-04 y
DEF-05).** Sobre la base cargada con
`python manage.py seed --reset` y con el servidor local en marcha:

1. Chromium headless (Playwright) abrió la aplicación real y se autenticó con los
   usuarios ficticios del seed (`estudiante1@example.com`,
   `estudiante2@example.com`, `bibliotecario1@example.com`).
2. Cada pantalla se capturó con la ventana fijada en 360×900 y 1280×900, sin
   modificar templates, datos ni estilos (`local/tools/capturas.py`). Las animaciones se desactivan con
   `prefers-reduced-motion`.
3. Las capturas de `../mockups/v2/` usan el mismo procedimiento con ventanas de
   360×1400 y 1280×1200.

Si la base está vacía o con datos de prueba, las pantallas se ven distintas: para
reproducirlas hay que ejecutar `python manage.py seed --reset` antes.

**Qué acredita.** Que las seis pantallas renderizan sin desbordes ni solapamientos
a 360, 768 y 1280 px, con la barra superior, los filtros, las tarjetas y la tabla
del día adaptándose según el sistema de diseño. Estas capturas son la evidencia de
CP-09 (RNF-02).

**Qué no acredita.** Estas capturas no sustituyen la auditoría; el cumplimiento
del RNF-02 se mide en `rnf-02/lighthouse/` (Lighthouse) y en `w3c/` (validador
del W3C).

## RNF-02 · Lighthouse

Carpeta `rnf-02/lighthouse/`. Seis auditorías el 2026-11-20 (tres pantallas ×
móvil y escritorio) con Lighthouse 12.8.2 sobre sesiones auténticas, mediante
`scripts/auditar_lighthouse.py`. Cada pantalla deja su informe `.report.html` y
`.report.json`; el consolidado está en `resumen.json`.

| Pantalla | Formato | Accesibilidad | Best Practices | Rendimiento | SEO |
|---|---|---|---|---|---|
| buscar | móvil / escritorio | 100 | 96 | 100 | 91 |
| mis-reservas | móvil / escritorio | 100 | 96 | 100 | 91 |
| bibliotecario | móvil / escritorio | 100 | 96 | 100 | 91 |

**Por qué importa.** Los hallazgos de DEF-04 salieron de aquí y del validador del
W3C; ninguno de los dos se había ejecutado antes en el proyecto.

## RNF-02 · Validación del W3C

Carpeta `w3c/`. Validación del HTML servido con el validador Nu (`vnu.jar`,
2026-11-20) sobre cinco pantallas: login, buscar, catálogo de libros, mis reservas
y panel. Resultado: **0 errores y 0 avisos** en las cinco. Un archivo `.json` por
pantalla con los mensajes del validador y `resumen.json` con el conteo.

## RNF-01 · Prueba de carga

Carpeta `rnf-01-estres/`. JMeter 5.6.3 contra gunicorn con 2 workers: 1, 10 y 50
usuarios concurrentes durante 60 s, más una prueba de reserva simultánea con 10
hilos sobre el mismo recurso. Incluye el método, la tabla de resultados, los
informes HTML de JMeter y las muestras `.jtl`. Ver `rnf-01-estres/README.md`.

## Flujo completo con Selenium

Carpeta `e2e/`. Seis capturas del recorrido automatizado (login, búsqueda,
reserva, QR, entrega y devolución) generadas por `scripts/prueba_e2e.py`, que
cubre CP-27 y falla si algún paso no coincide con lo esperado.

## Casos ejecutados (2026-11-13 a 2026-11-20)

27 de los 27 casos ejecutados y aprobados sobre el flujo real. Cada uno se
registra en `../qa/casos-prueba.md` con su resultado y la ruta de su evidencia.
CP-01 a CP-06 se re-ejecutaron el 2026-11-14 en el navegador; CP-07 y CP-11 a
CP-14 se ejecutaron el 2026-11-13 con el script local; CP-26 se ejecutó el
2026-11-19 en Chromium con y sin JavaScript, falló sin JavaScript (DEF-03) y se
repitió el 2026-11-20 tras la corrección.

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
| CP-26 | `CP-26.png`, `CP-26-reprueba.png` | Filtros reactivos con JavaScript; paso 5 sin JavaScript y su re-prueba tras DEF-03 |
| CP-08 | `CP-08.txt` | 20 peticiones de reserva + QR: 27 ms de promedio (RNF-01) |
| CP-09 | `rnf-02/`, `rnf-02/lighthouse/`, `w3c/` | Seis pantallas a 360 y 1280 px; Lighthouse con 100 en accesibilidad; 0 errores de marcado (RNF-02) |
| CP-27 | `e2e/` | Flujo completo automatizado con Selenium: 8 de 8 pasos correctos |

**Regeneración del cierre.** Las 23 capturas de casos se volvieron a ejecutar el
2026-11-20 sobre la versión final (`v1.0-final`), después de DEF-03, DEF-04 y
DEF-05, para que la evidencia coincida con el código entregado. En esa pasada se
corrigió el escenario de CP-01, que ahora filtra por tipo «Sala» como describen
sus pasos.

**Cómo se generaron.** CP-07 y CP-11 a CP-14 con `local/tools/ejecutar_cp.py`,
que reinicia el seed, recorre el flujo con el cliente de Django y captura la
pantalla resultante con Chromium a 1280×900. CP-01 a CP-06 se re-ejecutaron el
2026-11-14 en el navegador (Chromium) sobre la aplicación; la hora se fijó con
`DEMO_MODE`/`DEMO_NOW` para los casos de devolución. Las capturas de CP-01 a CP-06
se recortaron y rotularon por escenario (A/B); los rótulos son anotaciones y no
forman parte de la interfaz. CP-26 se ejecutó el 2026-11-19 con Chromium
(Playwright) sobre el flujo real, activando y desactivando JavaScript por
contexto de navegador; la re-prueba del paso 5 sin JavaScript se capturó el
2026-11-20. DEF-01 y DEF-02 son correcciones de los casos CP-01 y CP-23;
**DEF-03, DEF-04 y DEF-05 son defectos de producto** y los tres se cerraron con
su re-prueba. DEF-06 corrigió la evidencia de CP-01, que no reproducía el filtro
por tipo de sus pasos. Todo el detalle está en `../qa/defectos.md`.
