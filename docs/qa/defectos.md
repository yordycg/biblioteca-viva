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

## Resumen de ejecución

| Fecha | Casos ejecutados | Aprobados | Fallidos | Bloqueados | Ejecutado por |
|---|---|---|---|---|---|
| 2026-11-13 | 11 | 11 | 0 | 0 | Script local · Yordy Carmona |
| 2026-11-14 | 6 (CP-01 a CP-06, re-ejecución en navegador) | 6 | 0 | 0 | Gerald Sobarzo |
| 2026-11-17 | 12 (CP-10, CP-15 a CP-25) + CP-08 y CP-09 | 14 | 0 | 0 | Script local · verificó Gerald Sobarzo |

DEF-01 no altera el conteo de fallidos de la aplicación: es una corrección del
caso CP-01, registrada para dejar trazabilidad entre el criterio de semana 2 y el
RF-01 vigente.

## Observaciones de la ejecución del 2026-11-14 (no son defectos)

| Caso | Observación | Acción aplicada |
|---|---|---|
| CP-03 | El mensaje real es «Límite alcanzado: ya tienes 2 reservas activas para ese día.»; el caso esperaba «…para hoy.». | Resultado esperado ajustado al texto real. |
| CP-05 | A las 10:45 la búsqueda no ofrece el bloque 10:00–11:00 (ya iniciado), por lo que el paso 6 no se podía ejecutar en la búsqueda. | El paso 6 verifica la liberación en el inventario del panel. |
| CP-06 | El aviso real es «Devolución tardía: se aplicó una sanción de 7 días a Estudiante 1.»; el caso esperaba «Devolución tardía: Sanción de 7 días». | Resultado esperado ajustado al texto real. |
| CP-02 a CP-06 | Los pasos usaban «Seleccionar» y «Volver al inicio» de los mockups v1; la interfaz usa «Reservar bloque …» y «Buscar otro recurso». | Pasos actualizados a los textos de la interfaz vigente. |
| CP-04 | La interfaz no muestra la hora de inicio de la reserva. | Se eliminó la comparación de la hora; se verifica que la reserva permanezca En Uso. |
