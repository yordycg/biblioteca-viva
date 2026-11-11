# Semana 3 — Construcción y validación

> Artefactos evaluables de la semana 3 del proyecto BibliotecaViva.
> El flujo de trabajo interno vive en `local/` y no se versiona.

| Artefacto | Dónde |
|---|---|
| Sistema de diseño (SEM3-T1) | [`design/design-system.md`](design/design-system.md) |
| Mockups v2 (SEM3-T1) | [`mockups/`](mockups/) |
| Casos de prueba | [`qa/casos-prueba.md`](qa/casos-prueba.md) |
| Matriz de trazabilidad | [`qa/matriz-trazabilidad.md`](qa/matriz-trazabilidad.md) |
| Bitácora de defectos | [`qa/defectos.md`](qa/defectos.md) |
| Evidencias de ejecución | [`evidence/`](evidence/) |
| Capturas de interfaz 360/1280 (RNF-02) | [`evidence/rnf-02/`](evidence/rnf-02/) |

## Interfaz

El MVP usa los tokens y componentes del sistema de diseño institucional (paleta
IPVG, tipografía del sistema, badges de estado y medidor de cupo diario). La
implementación es **CSS propio** en `reservas/static/reservas/styles.css`: sin
Tailwind, sin CDN, sin fuentes ni imágenes remotas. La aplicación se ve igual sin
conexión a internet, requisito del entorno de evaluación.

Los mockups de `mockups/` son las láminas de Google Stitch que se usaron como
referencia. Las demás pantallas del rediseño no se conservaron como imagen porque
fueron renders de un lienzo de 1600 px con contenido móvil; su especificación
está en `design/design-system.md` y su resultado real se verifica en las capturas
de `evidence/`.

Los mockups usan un cuadrado amarillo con las iniciales «VG» como marcador de
posición. La implementación usa el **logo oficial del instituto** en la barra
superior y en la cabecera del login (procedencia, hash y paleta medida en
`design/design-system.md` §2.4 y §3).

## Orden de revisión

1. `design/design-system.md` — tokens, componentes y reglas de contenido.
2. `mockups/` — láminas de referencia.
3. `qa/` — casos y trazabilidad (estado real de cada uno).
4. `evidence/` — capturas a 360×800 y 1280×800.
