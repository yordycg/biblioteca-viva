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

## Ajustes posteriores a la revisión docente (MVP 1)

- El login ya no expone credenciales ni roles de demostración: se ingresa con correo institucional y las cuentas ficticias quedan documentadas en el `README.md` y en el manual.
- La búsqueda y la reserva rechazan fechas anteriores al día actual, tanto en el formulario como en una confirmación enviada por URL forzada.
- El panel del bibliotecario muestra el estado del inventario: contadores de recursos disponibles, reservados, en uso y no disponibles, más una tabla por recurso y bloque.

Cubierto por CP-15 y CP-16 y por `python manage.py test` (26 pruebas al cerrar el MVP 1).

## Ajustes posteriores a la revisión docente (MVP 2)

- Búsqueda unificada con pestañas **Salas y equipos** / **Libros**; el catálogo ya no es una pantalla aparte.
- Préstamo de libros por **3, 7 o 14 días**, con fecha de devolución, máximo 2 préstamos activos y un ejemplar por título.
- Ficha de libro en una sola tarjeta con carátula, datos bibliográficos, sinopsis, condiciones y panel de préstamo.
- `Reserva` distingue `BLOQUE` y `PRESTAMO`; QR, estados y sanción se reutilizan sin duplicar el flujo.

Cubierto por CP-18 y por `python manage.py test` (69 pruebas automáticas).

## Ventana de reserva (revisión del MVP 2)

- Para hoy solo se ofrecen bloques que comienzan al menos **15 minutos** después de la hora actual.
- La búsqueda y la confirmación rechazan bloques iniciados o sin antelación, incluso forzando la URL.
- El horizonte de reserva es de **7 días**; fuera de ese rango la fecha se rechaza.
- El selector de bloques se actualiza al cambiar la fecha sin recargar la página; sin JavaScript, el servidor aplica la misma regla.

Cubierto por CP-17 y por `python manage.py test` (69 pruebas automáticas).

## Catálogo inicial y horario 09:00–22:00

- Con fecha y bloque elegidos, la vista lista los recursos con su estado; el check **Solo disponibles** permite ocultar los ocupados.
- Los formularios validan al enviarse —con **Filtrar** o al cambiar un filtro ya completo—; los errores aparecen bajo el campo, con borde rojo.
- Los bloques pasan de 3 a **13 bloques de una hora**, de 09:00 a 22:00.
- Si la fecha elegida no tiene bloques disponibles, un aviso pide elegir otra fecha.
- El panel del bibliotecario muestra una **línea de tiempo** por recurso en lugar de una tabla de 13 columnas.

Cubierto por CP-17 y CP-20, con `python manage.py test` (69 pruebas automáticas).

## Panel del bibliotecario v2

- KPIs operativos: reservas de hoy, pendientes de entrega, en uso, préstamos de libros, vencen hoy, vencidos y sanciones activas.
- Agenda de próximas entregas y devoluciones de libros, con vencidos destacados.
- Ocupación agregada por los 13 bloques del día.
- Sanciones activas, no solo las aplicadas hoy.
- Filtros de la tabla por estado, bloque y búsqueda por código, recurso o usuario.
- El rol del usuario ya no se muestra en la barra superior.

Cubierto por CP-21, con `python manage.py test` (69 pruebas automáticas).

## Corrección S3 (cancelación, pestañas y filtros)

- **Cancelación de reservas**: el solicitante anula su reserva pendiente desde "Mis reservas" y el bibliotecario desde el panel. Solo aplica a reservas pendientes de entrega —una reserva En Uso se devuelve— y el panel exige un motivo.
- Se registra **quién, cuándo y por qué** (`cancelada_en`, `cancelada_por`, `motivo_cancelacion`); el solicitante solo puede cancelar antes de que empiece su bloque o su fecha de retiro, el bibliotecario puede hacerlo en cualquier momento para cubrir el no-show.
- Cancelar **libera el bloque y el cupo diario**, y el QR anterior se rechaza con un mensaje propio.
- **Pestañas en el panel**: Operación, Inventario, Reservas del día y Validación. La pestaña activa se conserva al validar, devolver, cancelar o filtrar, y buscar un código abre Validación.
- **Filtro del estado del inventario** por nombre, tipo y estado, con contador "Mostrando X de Y" y contadores globales intactos.
- **Filtros vacíos al entrar** y validación solo al enviar; el selector de bloque nunca se autoselecciona y un enlace con fecha y bloque sigue funcionando.
- **Filtros reactivos**: los selectores y casillas envían el formulario al cambiar; el botón "Filtrar" se mantiene para navegadores sin JavaScript y la búsqueda de texto no se autoenvía.
- **Seed con fecha relativa**: las reservas de ejemplo se programan en el primer bloque reservable de hoy (o de mañana) y `seed --fecha AAAA-MM-DD` permite fijarlas.

Cubierto por CP-20, CP-21 y CP-22 a CP-26, con `python manage.py test` (90 pruebas automáticas).

## Orden de revisión

1. `design/design-system.md` — tokens, componentes y reglas de contenido.
2. `mockups/` — láminas de referencia.
3. `qa/` — casos y trazabilidad (estado real de cada uno).
4. `evidence/` — capturas a 360×800 y 1280×800.
