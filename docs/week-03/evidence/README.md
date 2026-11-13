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
a 360 px y 1280 px, con la barra superior, los filtros, las tarjetas y la tabla
del día adaptándose según el sistema de diseño.

**Qué no acredita.** No es la ejecución de CP-09 ni reemplaza la medición de
Lighthouse: la accesibilidad (contraste, foco, navegación por teclado) se audita
en la semana 4 y se registra en su propio archivo.

## Casos ejecutados (2026-11-13)

Once casos ejecutados sobre el flujo real y aprobados. Cada uno se registra en
`../qa/casos-prueba.md` con su resultado y la ruta de su evidencia.

| Caso | Evidencia | Qué muestra |
|---|---|---|
| CP-01 | `CP-01.png` | Recursos libres del bloque con su estado |
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

**Cómo se generaron.** Con `local/tools/ejecutar_cp.py`, que reinicia el seed,
recorre el flujo con el cliente de Django y captura la pantalla resultante con
Chromium a 1280×900. La hora se fija con `DEMO_MODE`/`DEMO_NOW` para los casos de
devolución. La ejecución no encontró defectos.
