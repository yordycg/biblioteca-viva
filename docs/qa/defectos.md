# Bitácora de defectos — semana 3

> Registro de defectos encontrados al ejecutar los casos de prueba.
> Un defecto de la aplicación entra aquí **solo** si se reprodujo en ella; si un
> caso se ejecutó y no falló, no se inventa un hallazgo: se anota «sin defectos»
> en el resumen de la ejecución. También se registran los defectos de diseño de
> un caso (por ejemplo, un criterio desactualizado), marcados como «documentación».

## Cómo registrar

1. Asignar el siguiente ID libre: `DEF-01`, `DEF-02`, …
2. Escribir pasos reproducibles, con los datos exactos (usuario, recurso, fecha,
   bloque y código si aplica).
3. Severidad según el impacto, no según la molestia:
   - **Crítica:** bloquea el flujo principal o pierde datos.
   - **Alta:** una regla de negocio se cumple mal (RF-06, RF-07).
   - **Media:** mensaje o estado incorrecto que confunde, sin pérdida de datos.
   - **Baja:** documentación, texto, alineación o detalle visual.
4. Al corregir, enlazar el commit y **volver a ejecutar el caso** con los mismos
   datos. La columna «Re-prueba» solo se completa con esa nueva ejecución.

## Registro

### DEF-01 — CP-01 desactualizado respecto del RF-01 vigente

| Campo | Detalle |
|---|---|
| Descripción | CP-01 se diseñó en semana 2 contra un RF-01 que pedía listar únicamente los recursos libres. El RF-01 vigente (desde la semana 3) pide mostrar todos los recursos con su estado y permitir «Solo disponibles». La ejecución del 2026-11-14 mostró que la aplicación cumple el RF vigente: Sala 1 aparece como «Reservado» y desaparece al activar el filtro. No es un defecto de la aplicación; es un defecto de diseño del caso. |
| Pasos para reproducir | 1. Iniciar sesión como estudiante1@example.com. 2. Abrir «Buscar» → «Salas y equipos». 3. Elegir Tipo «Sala», fecha 2026-11-10 y bloque 10:00–11:00 (Sala 1 ya reservada por estudiante2@example.com). 4. Presionar «Filtrar» sin marcar «Solo disponibles». Resultado: «2 recursos»: Sala 1 «Reservado» y Sala 3 «Disponible». 5. Marcar «Solo disponibles» y filtrar: queda solo Sala 3. |
| Severidad | Baja (documentación): el comportamiento de la aplicación es correcto; el criterio del caso estaba desactualizado. |
| Caso asociado | CP-01 |
| Responsable | Gerald Sobarzo |
| Estado | Cerrado |
| Corrección (commit) | CP-01 actualizado al RF-01 vigente: resultado esperado y pasos ajustados a «todos los recursos con su estado» + «Solo disponibles». |
| Re-prueba | CP-01 re-evaluado con la evidencia del 2026-11-14 → Aprobado. |

### DEF-02 — CP-23 esperaba 404 para una cancelación por GET

| Campo | Detalle |
|---|---|
| Descripción | El paso 1 de CP-23 pedía abrir por URL `/mis-reservas/<id>/cancelar/` de una reserva ajena y esperaba 404. La vista tiene `@require_POST`, así que un GET responde 405 y no ejecuta nada; con POST la respuesta sí es 404. La aplicación es correcta: el caso describía el método equivocado. |
| Pasos para reproducir | 1. Iniciar sesión como estudiante1@example.com. 2. Abrir por GET `/mis-reservas/<id-de-estudiante2>/cancelar/`: responde 405. 3. Repetir con POST: responde 404 y la reserva no cambia. |
| Severidad | Baja (documentación): no hay efecto sobre datos. |
| Caso asociado | CP-23 |
| Responsable | Yordy Carmona |
| Estado | Cerrado |
| Corrección (commit) | CP-23 actualizado en la ejecución del 2026-11-17: el paso indica POST y se acepta 404; se documenta que GET responde 405. |
| Re-prueba | CP-23 re-ejecutado el 2026-11-17 → Aprobado. |

### DEF-03 — Sin JavaScript, «Filtrar» no funciona en «Salas y equipos»

| Campo | Detalle |
|---|---|
| Descripción | En Buscar › Salas y equipos, la lista de bloques horarios se llena con JavaScript al elegir la fecha. Sin JavaScript el selector queda solo con «Elige un bloque» y es obligatorio, de modo que el navegador impide enviar el formulario. El comentario de `app.js` indica que sin JavaScript los formularios siguen funcionando; en esta vista no se cumple. |
| Pasos para reproducir | 1. Desactivar JavaScript en el navegador. 2. Iniciar sesión como estudiante1@example.com. 3. Abrir «Buscar» › «Salas y equipos». 4. Escribir la fecha 2026-11-10. 5. Presionar «Filtrar». Resultado: aviso «Please select an item in the list.» en «Bloque horario», sin recarga ni resultados. |
| Severidad | Media: la función es inaccesible sin JavaScript, sin pérdida de datos; con JavaScript todo funciona. |
| Caso asociado | CP-26 (paso 5) |
| Responsable | Reportó Gerald Sobarzo · corrigió Yordy Carmona |
| Estado | Cerrado |
| Corrección (commit) | `c15e1c9` — `BusquedaForm` ofrece el catálogo de bloques cuando no hay fecha; el servidor sigue validando la disponibilidad en `clean()`. Regresión en `tests/test_interfaz.py` y `tests/test_inventario.py` (91 pruebas). |
| Re-prueba | 2026-11-20, Chromium (Playwright) con JavaScript desactivado: el selector muestra 14 opciones y «Filtrar» responde con los 4 recursos del bloque 10:00–11:00 → Aprobado (`docs/evidence/CP-26-reprueba.png`). |

## Resumen de ejecución

| Fecha | Casos ejecutados | Aprobados | Fallidos | Bloqueados | Ejecutado por |
|---|---|---|---|---|---|
| 2026-11-13 | 11 | 11 | 0 | 0 | Script local · Yordy Carmona |
| 2026-11-14 | 6 (CP-01 a CP-06, re-ejecución en navegador) | 6 | 0 | 0 | Gerald Sobarzo |
| 2026-11-17 | 12 (CP-10, CP-15 a CP-25) + CP-08 y CP-09 | 14 | 0 | 0 | Script local · verificó Gerald Sobarzo |
| 2026-11-19 | 1 (CP-26, navegador con y sin JavaScript) | 0 | 1 | 0 | Gerald Sobarzo |

DEF-01 no altera el conteo de fallidos de la aplicación: es una corrección del
caso CP-01, registrada para dejar trazabilidad entre el criterio de semana 2 y el
RF-01 vigente. DEF-02 tampoco es un defecto de la aplicación: corrige el método
HTTP descrito en CP-23. Los fallos reales contra el producto son **DEF-03**
(CP-26, ejecución del 2026-11-19), **DEF-04** y **DEF-05**, los tres cerrados con
su re-prueba el 2026-11-20. **DEF-06** es una corrección de la evidencia de CP-01,
detectada al regenerar las capturas. DEF-04 y DEF-05 los detectaron herramientas que no
se habían usado antes: Lighthouse 12.8.2 y el validador Nu del W3C.

| Fecha | Casos re-ejecutados | Aprobados | Fallidos | Bloqueados | Ejecutado por |
|---|---|---|---|---|---|
| 2026-11-20 | 1 (CP-26, paso 5 sin JavaScript) | 1 | 0 | 0 | Yordy Carmona |
| 2026-11-20 | 1 (CP-27, flujo E2E con Selenium) | 1 | 0 | 0 | Yordy Carmona |

### DEF-04 — Marcado HTML inválido detectado por el validador del W3C

| Campo | Detalle |
|---|---|
| Descripción | El validador Nu del W3C reportó dos hallazgos de marcado. (1) En «Buscar» y en el catálogo de libros, la sección de resultados usaba `aria-labelledby` pero no contenía un encabezado cuando no había búsqueda: «Section lacks heading». (2) En «Mis reservas», la lista de datos usaba `<dl>` con un `<div>` intermedio que contenía un `<span>` y otro `<div>`: «Element span not allowed as child of element div» y «div is missing a required instance of child element dt/dd» (8 errores por reserva mostrada). No afectaba la vista, pero el documento no era HTML válido. |
| Pasos para reproducir | 1. Iniciar sesión y abrir «Buscar» sin filtros.<br>2. Ejecutar `python scripts/validar_w3c.py`.<br>3. Abrir «Mis reservas» con al menos una reserva y repetir la validación. |
| Severidad | Baja: no hay pérdida de datos ni función inaccesible; afecta el cumplimiento de estándares. |
| Caso asociado | CP-09 |
| Responsable | Yordy Carmona |
| Estado | Cerrado |
| Corrección (commit) | `5691bf8` — encabezado oculto en la sección de resultados de ambas vistas; la lista de datos pasó a `div` con `span` de término y valor, y se ajustaron las reglas `.data-list__term` y `.data-list__value` en el CSS. |
| Re-prueba | 2026-11-20: `scripts/validar_w3c.py` sobre login, buscar, libros, mis-reservas y panel → **0 errores y 0 avisos** (`docs/evidence/w3c/`). |

### DEF-05 — La antelación mínima de 15 minutos no se explica antes de elegir el bloque

| Campo | Detalle |
|---|---|
| Descripción | La regla de antelación mínima (RF-01) solo aparecía cuando ya no quedaban bloques para la fecha elegida. El usuario no sabía por qué faltaban bloques ni cuánta antelación necesitaba: la explicación llegaba después del problema, no antes de la acción. |
| Pasos para reproducir | 1. Iniciar sesión como estudiante1@example.com.<br>2. Abrir «Buscar» › «Salas y equipos».<br>3. Revisar el campo «Bloque horario»: no hay texto de ayuda. |
| Severidad | Baja (UX): el sistema no falla y el mensaje posterior es correcto; se pierde claridad antes de la acción. |
| Caso asociado | CP-09 (usabilidad) |
| Responsable | Yordy Carmona |
| Estado | Cerrado |
| Corrección (commit) | `5691bf8` — texto de ayuda bajo el selector: «Solo se ofrecen bloques con al menos 15 minutos de antelación», con el valor tomado de `services.MIN_ANTELACION_MIN`. |
| Re-prueba | 2026-11-20: la ayuda se muestra en «Salas y equipos» antes de filtrar; el validador y las 91 pruebas automáticas siguen en verde. |

### DEF-06 — La captura de CP-01 no correspondía a los pasos del caso

| Campo | Detalle |
|---|---|
| Descripción | Los pasos de CP-01 indican filtrar por tipo «Sala» y esperar dos recursos (Sala 3 disponible y Sala 1 reservada), sin equipos. La herramienta de captura generaba la pantalla con el filtro en «Todos», de modo que la imagen mostraba cuatro recursos, incluidos el proyector y el notebook. El caso se declaraba aprobado con una evidencia que no reproducía su escenario. |
| Pasos para reproducir | 1. Ejecutar la captura de CP-01 con la herramienta de casos.<br>2. Abrir `docs/evidence/CP-01.png`.<br>3. Comparar con los pasos del caso: el filtro aparece en «Todos» y hay cuatro recursos. |
| Severidad | Baja (documentación): no afecta el producto; la evidencia no acreditaba lo que decía acreditar. |
| Caso asociado | CP-01 |
| Responsable | Yordy Carmona |
| Estado | Cerrado |
| Corrección (commit) | `cd72a25` — la captura envía `tipo=SALA` y verifica que ningún equipo aparezca en los resultados; la imagen regenerada muestra el filtro «Sala» y los dos recursos del bloque. |
| Re-prueba | 2026-11-20: captura regenerada sobre `v1.0-final`; filtro «Sala», dos recursos y la ayuda de antelación visible. |

El detector de DEF-04 y DEF-05 fue la combinación de Lighthouse 12.8.2 y el
validador Nu del W3C; ninguno de los dos se había ejecutado antes en el proyecto.
DEF-06 apareció al regenerar las capturas sobre la versión final: la evidencia no
coincidía con los pasos del caso.


## Observaciones de la ejecución del 2026-11-14 (no son defectos)

| Caso | Observación | Acción aplicada |
|---|---|---|
| CP-03 | El mensaje real es «Límite alcanzado: ya tienes 2 reservas activas para ese día.»; el caso esperaba «…para hoy.». | Resultado esperado ajustado al texto real. |
| CP-05 | A las 10:45 la búsqueda no ofrece el bloque 10:00–11:00 (ya iniciado), por lo que el paso 6 no se podía ejecutar en la búsqueda. | El paso 6 verifica la liberación en el inventario del panel. |
| CP-06 | El aviso real es «Devolución tardía: se aplicó una sanción de 7 días a Estudiante 1.»; el caso esperaba «Devolución tardía: Sanción de 7 días». | Resultado esperado ajustado al texto real. |
| CP-02 a CP-06 | Los pasos usaban «Seleccionar» y «Volver al inicio» de los mockups v1; la interfaz usa «Reservar bloque …» y «Buscar otro recurso». | Pasos actualizados a los textos de la interfaz vigente. |
| CP-04 | La interfaz no muestra la hora de inicio de la reserva. | Se eliminó la comparación de la hora; se verifica que la reserva permanezca En Uso. |
