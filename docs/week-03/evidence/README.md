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

**Cómo se generaron (2026-11-11).** Sobre la base `db.sqlite3` cargada con
`python manage.py seed --reset` y con `DEMO_MODE=1`, `DEMO_NOW=2026-11-10T10:30:00`:

1. Cada pantalla se solicitó con el cliente de pruebas de Django usando la sesión
   del rol correspondiente (`estudiante1@example.com`, `bibliotecario1@example.com`).
2. El HTML devuelto por la aplicación se guardó y se renderizó en Chromium
   headless con ventana de 360×900 y 1280×900; la hoja de estilos es la misma que
   sirve Django (`reservas/static/reservas/styles.css`).
3. Único cambio en el HTML: las rutas `/static/` se resolvieron como archivo local
   para el render, porque no había servidor HTTP levantado. No se modificó ningún
   template, dato ni estilo.

**Qué acredita.** Que las seis pantallas renderizan sin desbordes ni solapamientos
a 360 px y 1280 px, con la barra superior, los filtros, las tarjetas y la tabla
del día adaptándose según el sistema de diseño.

**Qué no acredita.** No es la ejecución de CP-09 ni reemplaza la medición de
Lighthouse: la accesibilidad (contraste, foco, navegación por teclado) se audita
en la semana 4 y se registra en su propio archivo.

## CP-01 a CP-14

Todavía no hay capturas. Cada caso se registra en `../qa/casos-prueba.md` con su
estado real; los archivos de esta carpeta se agregan al ejecutarlos.
