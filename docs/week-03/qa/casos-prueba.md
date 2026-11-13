# Casos de prueba — Biblioteca Viva (diseño SEM2-T6, ejecución semana 3)

Estado real: CP-01 a CP-12 se diseñaron en semana 2, antes de que existiera el código de F1–F3. CP-13 y CP-14 se agregaron en semana 3 al implementar la pantalla "Mis reservas". CP-15 y CP-16 se agregaron en la revisión docente del MVP 1 (fecha mínima e inventario del panel), CP-17 en la revisión del MVP 2 (ventana de reserva), CP-18 en la revisión del MVP 2 (catálogo de libros) y CP-21 en la revisión del panel del bibliotecario. Todos los resultados, estados y fechas de ejecución siguen en Pendiente: no hay ejecuciones, capturas ni métricas registradas.

La interfaz del MVP se rediseñó en la semana 3 con el sistema de diseño institucional (`docs/week-03/design/design-system.md`). Ese cambio **no** convierte ningún caso en aprobado: los resultados siguen en Pendiente hasta que QA ejecute cada CP y adjunte su evidencia.

Fuentes usadas: requisitos RF/RNF del equipo, diagrama de casos de uso (CU0–CU6) y mockups [SEM2-T1] (Pantalla 1, Pantalla 2 y Vista Bibliotecario). Los textos de botones y mensajes salen de esos mockups; lo que los mockups no definen queda como [COMPLETAR] o [VERIFICAR].

## Datos de prueba comunes (ficticios)

| Dato | Valor |
|---|---|
| Fecha de prueba | 2026-11-10 |
| Solicitante | estudiante1@example.com (contraseña ficticia del seed) |
| Otro solicitante | estudiante2@example.com |
| Resolutor (bibliotecario) | bibliotecario1@example.com |
| Recursos semilla | Sala 3 (Piso 1, 8 personas) · Sala 1 (Piso 1, 4 personas) · Proyector Epson (eq-014) · Notebook Dell (eq-002) |
| Libros semilla | Don Quijote de la Mancha · Martín Fierro · La Araucana · Veinte mil leguas de viaje submarino · La metamorfosis · Frankenstein (carátulas SVG locales) |
| Bloques | 10:00–11:00 · 11:00–12:00 · 15:00–16:00 |
| Formato de ID de reserva | RSV-NNNN (ej. RSV-0042) |

Convención: cada caso parte del *seed* reiniciado (sin reservas ni sanciones), salvo lo indicado en sus precondiciones. Estados de reserva: Reservada, En Uso, Finalizada.

## Referencias de interfaz (de los mockups)

| Elemento | Texto en el mockup |
|---|---|
| Navegación del solicitante (móvil) | Pestañas "Buscar", "Mis Reservas", "Historial" |
| Filtros de búsqueda | "Tipo de recurso", "Fecha", "Bloque horario", botón "Buscar" |
| Resultado de búsqueda | Tarjeta con etiqueta "Disponible" y botón "Seleccionar" |
| Detalle de reserva | Botón "Confirmar reserva" |
| Reserva confirmada | "¡Reserva Confirmada!", etiqueta "Reservada", QR, "ID reserva: RSV-NNNN", botones "Descargar QR" / "Volver al Inicio" |
| Tope diario (RF-06) | "Límite alcanzado: Ya tienes 2 reservas activas para hoy." + botón "Volver al inicio" |
| Vista Resolutor | Visor de cámara con QR, tarjeta con ID, recurso, correo y Estado; botones "Confirmar entrega" y "Registrar devolución" |
| Sanción (RF-07) | Banner "Devolución tardía: Sanción de 7 días" |

Vacíos detectados en los mockups v1 y cómo se resolvieron en la implementación de semana 3:

| Vacío del mockup | Resolución implementada |
|---|---|
| No hay mensaje para QR inválido ni duplicado ([COMPLETAR] en CP-04) | El panel muestra `No existe una reserva con el código …` y `QR ya utilizado o la reserva no está vigente.` |
| No hay campo para ingresar el código manualmente ([VERIFICAR] en CP-04) | El panel incluye el campo «Código del QR o identificador de reserva» con ingreso manual |
| No hay mensaje para un usuario sancionado ([COMPLETAR] en CP-06) | La búsqueda muestra el aviso «Sanción vigente» con la fecha de término |
| Bloques de 90 min en el mockup ([VERIFICAR]) | Se mantienen bloques de 60 min: `10:00-11:00`, `11:00-12:00`, `15:00-16:00` |
| No hay pantalla de «Mis reservas» ([VERIFICAR] en CP-13) | Se implementó con secciones Activas e Historial y botón «Ver QR» |

Referencias de interfaz vigentes: ver `design/design-system.md` §3 (componentes) y §4 (reglas de contenido).

## CP-01 — Búsqueda de recurso disponible

| Campo | Detalle |
|---|---|
| Requisito asociado | RF-01 (CU1 Buscar recurso) |
| Tipo | Positivo |
| Precondiciones | Seed cargado. Sala 3 libre el 2026-11-10 en 10:00–11:00. Sala 1 con reserva activa de estudiante2@example.com en ese mismo bloque. |
| Datos de entrada | Usuario: estudiante1@example.com · Tipo de recurso: Sala · Fecha: 2026-11-10 · Bloque horario: 10:00–11:00 |
| Pasos | 1. Iniciar sesión como estudiante1@example.com.<br>2. Abrir la pestaña "Buscar".<br>3. Elegir Tipo de recurso "Sala", Fecha 2026-11-10 y Bloque horario 10:00–11:00.<br>4. Presionar "Buscar".<br>5. Revisar el encabezado y las tarjetas de resultados. |
| Resultado esperado | El listado muestra únicamente Sala 3 con etiqueta "Disponible" y botón "Seleccionar". Sala 1 (ocupada) no aparece. No aparecen Proyector ni Notebook (tipo distinto). El encabezado indica fecha y bloque consultados y la cantidad de resultados coincide con las tarjetas mostradas. |
| Resultado obtenido | Recursos libres del bloque listados con su estado. |
| Estado | Aprobado |
| Evidencia | `docs/week-03/evidence/CP-01.png` |
| Ejecutado por / fecha | Script local · Yordy Carmona / 2026-11-13 |

## CP-02 — Reserva exitosa y generación de QR

| Campo | Detalle |
|---|---|
| Requisito asociado | RF-02, RF-03 (CU2 Reservar recurso, CU3 Visualizar QR) |
| Tipo | Positivo |
| Precondiciones | Seed cargado. Sala 3 libre el 2026-11-10 en 10:00–11:00. estudiante1@example.com sin reservas ese día. |
| Datos de entrada | Usuario: estudiante1@example.com · Recurso: Sala 3 · Fecha: 2026-11-10 · Bloque: 10:00–11:00 |
| Pasos | 1. Iniciar sesión como estudiante1@example.com.<br>2. Buscar Sala, 2026-11-10, 10:00–11:00 (como en CP-01).<br>3. Presionar "Seleccionar" en Sala 3.<br>4. En el detalle (Estado: Disponible), presionar "Confirmar reserva".<br>5. Anotar el "ID reserva" mostrado (formato RSV-NNNN).<br>6. Verificar que se muestran "¡Reserva Confirmada!", la etiqueta "Reservada" y el QR.<br>7. Decodificar el QR con un lector externo y comparar su contenido con el ID anotado.<br>8. Presionar "Volver al Inicio" y repetir la búsqueda del paso 2. |
| Resultado esperado | Reserva registrada con estado Reservada. Se muestra un QR único cuyo contenido decodificado incluye el ID de la reserva, junto con el resumen del recurso y su horario. En la nueva búsqueda, Sala 3 ya no aparece para 10:00–11:00. |
| Resultado obtenido | Reserva RSV-0156 registrada con su QR. |
| Estado | Aprobado |
| Evidencia | `docs/week-03/evidence/CP-02.png` |
| Ejecutado por / fecha | Script local · Yordy Carmona / 2026-11-13 |

## CP-03 — Tercera reserva del mismo día rechazada

| Campo | Detalle |
|---|---|
| Requisito asociado | RF-06 (CU2 Reservar recurso) |
| Tipo | Límite |
| Precondiciones | Seed cargado. estudiante1@example.com tiene 2 reservas activas el 2026-11-10: Sala 3 10:00–11:00 (ID-A) y Sala 3 11:00–12:00 (ID-B). Sala 3 libre en 15:00–16:00. |
| Datos de entrada | Usuario: estudiante1@example.com · Recurso: Sala 3 · Fecha: 2026-11-10 · Bloque: 15:00–16:00 (3ª reserva) |
| Pasos | 1. Iniciar sesión como estudiante1@example.com.<br>2. Abrir "Mis Reservas" y confirmar las 2 reservas activas (ID-A, ID-B).<br>3. En "Buscar", elegir Sala, 2026-11-10, 15:00–16:00 y presionar "Buscar".<br>4. Presionar "Seleccionar" en Sala 3 y luego "Confirmar reserva".<br>5. Leer el mensaje mostrado.<br>6. Presionar "Volver al inicio", abrir "Mis Reservas" y revisar las reservas.<br>7. Repetir la búsqueda del paso 3. |
| Resultado esperado | La 3ª reserva se rechaza con el mensaje "Límite alcanzado: Ya tienes 2 reservas activas para hoy." [VERIFICAR texto: el mockup dice "hoy"; la fecha de prueba es 2026-11-10]. "Mis Reservas" muestra solo ID-A e ID-B, con los mismos datos y estado Reservada. Sala 3 sigue disponible en 15:00–16:00. |
| Resultado obtenido | Tercera reserva rechazada; quedan 2 activas. |
| Estado | Aprobado |
| Evidencia | `docs/week-03/evidence/CP-03.png` |
| Ejecutado por / fecha | Script local · Yordy Carmona / 2026-11-13 |

## CP-04 — QR inválido o duplicado rechazado

| Campo | Detalle |
|---|---|
| Requisito asociado | RF-04 (CU4 Validar inicio) |
| Tipo | Negativo |
| Precondiciones | Seed cargado. Reserva Reservada de estudiante1@example.com para Sala 3, 2026-11-10 10:00–11:00, con ID anotado como ID-RESERVA. Hora actual dentro del bloque (ej. 10:05) [VERIFICAR mecanismo para fijar la hora]. Sesión como bibliotecario1@example.com en la vista Resolutor. |
| Datos de entrada | Escenario A (inválido): código NO-EXISTE. Escenario B (duplicado): código de ID-RESERVA ya iniciada. |
| Pasos | Escenario A — QR inválido<br>1. Abrir el visor de validación de la vista Resolutor.<br>2. Ingresar el código NO-EXISTE [VERIFICAR: ingreso manual, el mockup solo muestra cámara].<br>3. Leer el mensaje y verificar que ID-RESERVA sigue en estado Reservada.<br>Escenario B — QR duplicado<br>4. Ingresar el código de ID-RESERVA; en la tarjeta (ID, recurso, correo, Estado "Reservada") presionar "Confirmar entrega". La reserva pasa a En Uso; anotar la hora de inicio.<br>5. Ingresar nuevamente el mismo código de ID-RESERVA.<br>6. Leer el mensaje y verificar que la reserva sigue En Uso con la misma hora de inicio. |
| Resultado esperado | A: se rechaza NO-EXISTE con mensaje de QR inválido [COMPLETAR texto]; no se muestra tarjeta de reserva y ninguna reserva cambia de estado. B: el primer ingreso deja la reserva En Uso; el segundo se rechaza con mensaje de QR ya utilizado [COMPLETAR texto] y la reserva permanece En Uso, sin cambios en su hora de inicio. |
| Resultado obtenido | QR inexistente y segundo uso del mismo QR rechazados. |
| Estado | Aprobado |
| Evidencia | `docs/week-03/evidence/CP-04.png` (captura de ambos mensajes; si hace falta, dos capturas con sufijo -A y -B) |
| Ejecutado por / fecha | Script local · Yordy Carmona / 2026-11-13 |

## CP-05 — Devolución dentro del bloque horario

| Campo | Detalle |
|---|---|
| Requisito asociado | RF-05 (CU5 Registrar devolución) |
| Tipo | Positivo |
| Precondiciones | Seed cargado. Reserva de estudiante1@example.com para Sala 3, 2026-11-10 10:00–11:00, en estado En Uso (inicio validado como en CP-04). Hora de devolución: 10:45 [VERIFICAR mecanismo para fijar la hora]. Sesión como bibliotecario1@example.com. |
| Datos de entrada | Código de la reserva En Uso (RSV-NNNN) · Hora de devolución: 10:45 |
| Pasos | 1. Iniciar sesión como bibliotecario1@example.com.<br>2. En el visor, ingresar o escanear el QR de la reserva En Uso.<br>3. Verificar en la tarjeta: ID, Sala 3, correo y Estado "En Uso".<br>4. Presionar "Registrar devolución" (hora 10:45).<br>5. Verificar el estado de la reserva.<br>6. Buscar como estudiante1@example.com: Sala, 2026-11-10, 10:00–11:00.<br>7. Intentar una reserva nueva de Sala 1, 15:00–16:00. |
| Resultado esperado | La reserva pasa a Finalizada. Sala 3 vuelve a aparecer disponible en la búsqueda. No aparece el banner de sanción. estudiante1@example.com puede reservar normalmente (paso 7), sin sanción. |
| Resultado obtenido | RSV-0166 quedó Finalizada sin sanción. |
| Estado | Aprobado |
| Evidencia | `docs/week-03/evidence/CP-05.png` |
| Ejecutado por / fecha | Script local · Yordy Carmona / 2026-11-13 |

## CP-06 — Devolución 1 minuto después del bloque → sanción

| Campo | Detalle |
|---|---|
| Requisito asociado | RF-07 (CU5 Registrar devolución, CU6 Aplicar sanción) |
| Tipo | Límite |
| Precondiciones | Seed reiniciado. Reserva de estudiante1@example.com para Sala 3, 2026-11-10 10:00–11:00, en estado En Uso. Hora de devolución: 11:01 [VERIFICAR mecanismo para fijar la hora]. Sesión como bibliotecario1@example.com. Sala 1 libre en 15:00–16:00. |
| Datos de entrada | Código de la reserva En Uso · Hora de devolución: 11:01 (el bloque termina a las 11:00) · Reserva posterior: Sala 1, 2026-11-10, 15:00–16:00 |
| Pasos | 1. Iniciar sesión como bibliotecario1@example.com.<br>2. Ingresar o escanear el QR de la reserva En Uso y verificar la tarjeta.<br>3. Presionar "Registrar devolución" (hora 11:01).<br>4. Verificar que aparece el banner "Devolución tardía: Sanción de 7 días" y que la reserva queda Finalizada.<br>5. Verificar el registro de sanción de estudiante1@example.com (estado "Sancionado", fecha de término) [VERIFICAR dónde se ve].<br>6. Cerrar sesión e iniciar como estudiante1@example.com.<br>7. Buscar Sala 1, 2026-11-10, 15:00–16:00 e intentar reservar ("Seleccionar" → "Confirmar reserva").<br>8. Leer el mensaje mostrado. |
| Resultado esperado | La reserva pasa a Finalizada. Se muestra "Devolución tardía: Sanción de 7 días" y estudiante1@example.com queda "Sancionado" por 7 días (hasta 2026-11-17 [VERIFICAR regla de cómputo]). El intento de reserva del paso 7 se rechaza con mensaje que indica la sanción vigente [COMPLETAR texto]. |
| Resultado obtenido | Devolución a las 11:01: Finalizada y sanción de 7 días. |
| Estado | Aprobado |
| Evidencia | `docs/week-03/evidence/CP-06.png` |
| Ejecutado por / fecha | Script local · Yordy Carmona / 2026-11-13 |

## CP-07 — Login rechazado y acceso según el rol

| Campo | Detalle |
|---|---|
| Requisito asociado | RF-08 (CU0 Iniciar Sesión) |
| Tipo | Negativo |
| Precondiciones | Seed cargado. Sin sesión iniciada. |
| Datos de entrada | `estudiante1@example.com` con clave incorrecta · `estudiante1@example.com` con `demo1234` · `bibliotecario1@example.com` con `demo1234` |
| Pasos | 1. Abrir `/login/`.<br>2. Ingresar el correo de estudiante con una clave incorrecta.<br>3. Verificar el mensaje mostrado.<br>4. Ingresar con la clave correcta.<br>5. Verificar la vista de destino.<br>6. Cerrar sesión e ingresar como bibliotecario.<br>7. Verificar la vista de destino. |
| Resultado esperado | Las credenciales inválidas se rechazan con “Correo o contraseña incorrectos”; el estudiante llega a `/buscar/` y el bibliotecario a `/bibliotecario/`. |
| Resultado obtenido | Credenciales inválidas rechazadas; cada rol llega a su vista. |
| Estado | Aprobado |
| Evidencia | `docs/week-03/evidence/CP-07.png` |
| Ejecutado por / fecha | Script local · Yordy Carmona / 2026-11-13 |

## CP-08 — Reserva y QR dentro de 1,5 s

| Campo | Detalle |
|---|---|
| Requisito asociado | RNF-01 |
| Tipo | Límite |
| Precondiciones | Seed cargado. Servidor local en marcha. `scripts/medir_rendimiento.py` disponible. |
| Datos de entrada | 20 peticiones de reserva con generación de QR |
| Pasos | 1. Reiniciar los datos con `python manage.py seed --reset`.<br>2. Ejecutar `python scripts/medir_rendimiento.py`.<br>3. Registrar promedio, máximo y cantidad de peticiones.<br>4. Repetir la medición si el equipo estaba bajo carga. |
| Resultado esperado | El promedio de las 20 peticiones es menor o igual a 1,5 s, con el máximo registrado en la salida. |
| Resultado obtenido | Pendiente |
| Estado | Pendiente |
| Evidencia | `docs/week-03/evidence/CP-08.txt` |
| Ejecutado por / fecha | Pendiente |

## CP-09 — Interfaz responsiva y accesibilidad

| Campo | Detalle |
|---|---|
| Requisito asociado | RNF-02 |
| Tipo | Positivo |
| Precondiciones | Servidor local en marcha. Chromium y Lighthouse disponibles. |
| Datos de entrada | Resoluciones 360×800, 768×1024 y 1280×800 · Auditoría Lighthouse |
| Pasos | 1. Abrir “Buscar”, “Mis reservas” y el panel en las tres resoluciones.<br>2. Verificar que no aparezca scroll horizontal ni texto cortado.<br>3. Ejecutar Lighthouse sobre `/buscar/` y `/bibliotecario/`.<br>4. Registrar los puntajes de Accesibilidad y Best Practices. |
| Resultado esperado | Las tres pantallas se adaptan sin desbordes y los puntajes de Accesibilidad y Best Practices son mayores o iguales a 90. |
| Resultado obtenido | Pendiente |
| Estado | Pendiente |
| Evidencia | `docs/week-03/evidence/CP-09.png` |
| Ejecutado por / fecha | Pendiente |

## CP-10 — Contraseñas con hash y datos ficticios

| Campo | Detalle |
|---|---|
| Requisito asociado | RNF-03 |
| Tipo | Positivo |
| Precondiciones | Seed cargado. Repositorio clonado. |
| Datos de entrada | Usuarios del seed · `.gitignore` · búsqueda de correos y dominios reales |
| Pasos | 1. Inspeccionar el campo `password` de los usuarios del seed.<br>2. Verificar el prefijo del hash.<br>3. Revisar `.gitignore` (`.env`, `local/`, `db.sqlite3`).<br>4. Buscar correos y dominios reales en el repo. |
| Resultado esperado | Las contraseñas usan `pbkdf2_sha256`, no hay credenciales ni bases versionadas y todos los datos son `@example.com`. |
| Resultado obtenido | Pendiente |
| Estado | Pendiente |
| Evidencia | `docs/week-03/evidence/CP-10.md` |
| Ejecutado por / fecha | Pendiente |

## CP-11 — Búsqueda sin resultados

| Campo | Detalle |
|---|---|
| Requisito asociado | RF-01 (CU1 Buscar recurso) |
| Tipo | Negativo |
| Precondiciones | Seed cargado. Todas las salas ocupadas en el bloque elegido. Sesión como estudiante1@example.com. |
| Datos de entrada | Fecha y bloque del día · Tipo “Sala” · “Solo disponibles” activado |
| Pasos | 1. Abrir “Buscar” y la pestaña “Salas y equipos”.<br>2. Elegir la fecha y el bloque donde las salas están ocupadas.<br>3. Seleccionar el tipo “Sala”.<br>4. Activar “Solo disponibles”.<br>5. Verificar el mensaje y la ausencia de botones de reserva. |
| Resultado esperado | Se muestra un mensaje claro de que no hay resultados, sin error técnico ni trazas, y sin botón para reservar. |
| Resultado obtenido | Sin salas libres: mensaje claro y sin botones de reserva. |
| Estado | Aprobado |
| Evidencia | `docs/week-03/evidence/CP-11.png` |
| Ejecutado por / fecha | Script local · Yordy Carmona / 2026-11-13 |

## CP-12 — Devolución exactamente en la hora límite

| Campo | Detalle |
|---|---|
| Requisito asociado | RF-07 (CU5 Registrar devolución) |
| Tipo | Límite |
| Precondiciones | Reserva de 10:00–11:00 en estado En Uso. Hora de la aplicación fijada en 11:00 (`DEMO_MODE=1`, `DEMO_NOW=2026-11-12T11:00:00`). Sesión como bibliotecario1@example.com. |
| Datos de entrada | Código de la reserva En Uso · Devolución a las 11:00 exactas |
| Pasos | 1. Iniciar sesión como bibliotecario1@example.com.<br>2. Validar el código de la reserva En Uso.<br>3. Registrar la devolución con la hora fijada en 11:00.<br>4. Verificar el estado de la reserva.<br>5. Verificar que el solicitante no quedó sancionado.<br>6. Intentar una reserva nueva con ese usuario. |
| Resultado esperado | La reserva queda Finalizada y no se aplica sanción: el límite es el fin del bloque inclusive. El usuario puede volver a reservar. |
| Resultado obtenido | Devolución a las 11:00 exactas: Finalizada y sin sanción. |
| Estado | Aprobado |
| Evidencia | `docs/week-03/evidence/CP-12.png` |
| Ejecutado por / fecha | Script local · Yordy Carmona / 2026-11-13 |

## CP-13 — Mis reservas lista las reservas del usuario y reabre su QR

| Campo | Detalle |
|---|---|
| Requisito asociado | RF-02, RF-03 (CU2 Reservar recurso, CU3 Visualizar QR) |
| Tipo | Positivo |
| Precondiciones | Seed cargado. estudiante1@example.com con 1 reserva activa (Sala 3, 2026-11-10 10:00–11:00, ID-A) y 1 reserva finalizada (Sala 1, 2026-11-09 11:00–12:00). Sesión iniciada como estudiante1@example.com. |
| Datos de entrada | Usuario: estudiante1@example.com · Reserva activa: ID-A (RSV-NNNN) |
| Pasos | 1. Iniciar sesión como estudiante1@example.com.<br>2. Abrir "Mis reservas" en la navegación.<br>3. En la sección "Activas", verificar ID-A, recurso, fecha, bloque y estado "Reservada".<br>4. En la sección "Historial", verificar la reserva finalizada con estado "Finalizada".<br>5. Presionar "Ver QR" en ID-A.<br>6. Comparar el código mostrado con el ID de la reserva.<br>7. Presionar "Mis reservas" para volver a la lista. |
| Resultado esperado | "Mis reservas" muestra solo las reservas del usuario: ID-A en "Activas" con estado Reservada y la reserva finalizada en "Historial". El botón "Ver QR" abre el QR de ID-A y el código coincide con el ID de la reserva. Al volver, la lista se mantiene. |
| Resultado obtenido | RSV-0180 listada con acceso a su QR. |
| Estado | Aprobado |
| Evidencia | `docs/week-03/evidence/CP-13.png` |
| Ejecutado por / fecha | Script local · Yordy Carmona / 2026-11-13 |

## CP-14 — Un usuario no puede ver ni abrir el QR de una reserva ajena

| Campo | Detalle |
|---|---|
| Requisito asociado | RF-03, RF-08 (CU3 Visualizar QR, CU0 Iniciar Sesión) |
| Tipo | Negativo |
| Precondiciones | Seed cargado. Reserva de estudiante1@example.com para Sala 3, 2026-11-10 10:00–11:00 (ID-A). Sesión como estudiante2@example.com, sin reservas. |
| Datos de entrada | Usuario: estudiante2@example.com · URL forzada: `/reserva/<ID-A>/qr/` |
| Pasos | 1. Iniciar sesión como estudiante1@example.com y anotar el ID de su reserva (ID-A).<br>2. Cerrar sesión e iniciar como estudiante2@example.com.<br>3. Abrir "Mis reservas" y verificar que ID-A no aparece.<br>4. Escribir en el navegador la URL `/reserva/<ID-A>/qr/`.<br>5. Leer la respuesta del sistema. |
| Resultado esperado | "Mis reservas" de estudiante2@example.com muestra el estado vacío o solo sus propias reservas, sin ID-A. La URL forzada no expone el QR ajeno: el sistema responde 404 (no encontrado) y no muestra datos de la reserva de estudiante1@example.com. |
| Resultado obtenido | El QR ajeno responde 404 y no aparece en la lista. |
| Estado | Aprobado |
| Evidencia | `docs/week-03/evidence/CP-14.png` |
| Ejecutado por / fecha | Script local · Yordy Carmona / 2026-11-13 |

## CP-15 — Búsqueda y reserva con fecha pasada rechazadas

| Campo | Detalle |
|---|---|
| Requisito asociado | RF-01, RF-02 (CU1 Buscar recurso, CU2 Reservar recurso) |
| Tipo | Negativo |
| Precondiciones | Seed cargado. Sesión iniciada como estudiante1@example.com. La fecha de hoy es posterior a la fecha usada como dato (por ejemplo, hoy 2026-11-12 y dato 2026-11-09). |
| Datos de entrada | Tipo: Sala · Fecha: 2026-11-09 (anterior a hoy) · Bloque: 10:00–11:00 · URL forzada de confirmación: `/reservar/<ID-Sala-3>/?fecha=2026-11-09&bloque=10:00-11:00` |
| Pasos | 1. Abrir "Buscar".<br>2. Elegir Sala, fecha 2026-11-09 y bloque 10:00–11:00; presionar "Filtrar".<br>3. Leer el mensaje y verificar que no hay tarjetas de resultados.<br>4. Abrir la URL forzada de confirmación de Sala 3 con la misma fecha y presionar "Confirmar reserva".<br>5. Revisar "Mis reservas" y el contador de reservas del día. |
| Resultado esperado | La búsqueda muestra «La fecha no puede ser anterior a hoy. Elige hoy o un día posterior.» y no lista recursos. La confirmación por URL forzada tampoco crea la reserva: no aparece un ID nuevo, no se genera QR y no cambia la disponibilidad. El campo Fecha expone `min` con la fecha actual. |
| Resultado obtenido | Pendiente |
| Estado | Pendiente |
| Evidencia | `docs/week-03/evidence/CP-15.png` |
| Ejecutado por / fecha | Pendiente |

## CP-16 — Panel del bibliotecario muestra el estado del inventario

| Campo | Detalle |
|---|---|
| Requisito asociado | RF-04, RF-05 (CU4 Validar inicio, CU5 Registrar devolución) |
| Tipo | Positivo |
| Precondiciones | Seed cargado. Sala 3 con reserva Reservada hoy 10:00–11:00; Proyector Epson En Uso hoy 11:00–12:00; Notebook Dell marcado No disponible; Sala 1 libre todo el día. Sesión como bibliotecario1@example.com. |
| Datos de entrada | Fecha del panel: hoy · Recursos: 4 |
| Pasos | 1. Iniciar sesión como bibliotecario1@example.com.<br>2. Abrir "Panel".<br>3. Leer las tarjetas de resumen: Recursos, Disponibles hoy, Reservados, En uso y No disponibles.<br>4. Revisar la tabla "Estado del inventario" por recurso y por bloque.<br>5. Comparar los valores con las reservas registradas y con el estado del catálogo.<br>6. Registrar una devolución y volver al panel. |
| Resultado esperado | Las tarjetas muestran 4 recursos: 1 disponible, 1 reservado, 1 en uso y 1 no disponible; la ocupación del día es 50%. La tabla muestra un badge por bloque (Disponible, Reservado, En uso, No disponible) y el solicitante de cada reserva. Tras la devolución, el recurso pasa a Disponible y los contadores se actualizan. |
| Resultado obtenido | Pendiente |
| Estado | Pendiente |
| Evidencia | `docs/week-03/evidence/CP-16.png` |
| Ejecutado por / fecha | Pendiente |

## CP-17 — Ventana de reserva: bloques futuros, antelación y horizonte

| Campo | Detalle |
|---|---|
| Requisito asociado | RF-01, RF-02 (CU1 Buscar recurso, CU2 Reservar recurso) |
| Tipo | Límite |
| Precondiciones | Hora de la aplicación fijada en 2026-11-12 10:50. Sala 3 libre. Sesión como estudiante1@example.com. |
| Datos de entrada | Fecha hoy · Bloques de 09:00 a 22:00; 10:00–11:00 (ya iniciado), 11:00–12:00 (10 min de antelación) y 12:00–13:00 (más de 15 min) · Fecha hoy + 7 días · Fecha hoy + 8 días |
| Pasos | 1. Abrir "Buscar" con la fecha de hoy.<br>2. Revisar el selector de bloque: 13 opciones de 09:00 a 22:00; no debe ofrecer 10:00–11:00 ni 11:00–12:00; sí desde 12:00–13:00.<br>3. Forzar la URL de confirmación con 10:00–11:00 y verificar que no se crea la reserva.<br>4. Confirmar una reserva para hoy 12:00–13:00.<br>5. Repetir la búsqueda con hoy + 7 días y con hoy + 8 días. |
| Resultado esperado | Hoy solo se ofrecen bloques que comienzan al menos 15 minutos después de la hora actual; un bloque ya iniciado o con menos antelación se rechaza también en el servidor. La reserva de 12:00–13:00 se crea con su QR. La fecha hoy + 7 se acepta y hoy + 8 se rechaza con mensaje de horizonte. |
| Resultado obtenido | Pendiente |
| Estado | Pendiente |
| Evidencia | `docs/week-03/evidence/CP-17.png` |
| Ejecutado por / fecha | Pendiente |

## CP-18 — Catálogo, ficha y reserva de un libro

| Campo | Detalle |
|---|---|
| Requisito asociado | RF-01, RF-02 (CU1 Buscar recurso, CU2 Reservar recurso) |
| Tipo | Positivo |
| Precondiciones | Seed cargado. "Don Quijote de la Mancha" sin préstamos activos. Sesión como estudiante1@example.com. |
| Datos de entrada | Filtro del catálogo: "Cervantes" · Libro: Don Quijote de la Mancha · Fecha de retiro: hoy · Duración: 7 días |
| Pasos | 1. Iniciar sesión como estudiante1@example.com.<br>2. Abrir la pestaña "Libros" de "Buscar".<br>3. Escribir "Cervantes" en el filtro y presionar "Filtrar".<br>4. Verificar que se muestra la tarjeta con carátula, autor y año.<br>5. Abrir la ficha del libro.<br>6. Revisar ISBN, editorial, páginas, ubicación y sinopsis.<br>7. Elegir fecha de retiro y duración de 7 días.<br>8. Confirmar el préstamo y anotar el código RSV-NNNN.<br>9. Volver a la ficha y a "Mis reservas". |
| Resultado esperado | La pestaña de libros filtra por autor y muestra la carátula local. La ficha presenta los datos bibliográficos y el panel de préstamo. El préstamo genera un QR único, descuenta el cupo de préstamos y aparece en "Mis reservas" con autor y fecha de devolución. |
| Resultado obtenido | Pendiente |
| Estado | Pendiente |
| Evidencia | `docs/week-03/evidence/CP-18.png` |
| Ejecutado por / fecha | Pendiente |

## CP-19 — Préstamos de libros: solapamiento y límite de activos

| Campo | Detalle |
|---|---|
| Requisito asociado | RF-02, RF-06 (CU2 Reservar recurso) |
| Tipo | Límite |
| Precondiciones | Seed cargado. "Don Quijote de la Mancha" y "Martín Fierro" sin préstamos. Sesión como estudiante1@example.com. |
| Datos de entrada | Préstamo 1: Don Quijote, hoy, 7 días · Préstamo 2: Martín Fierro, hoy, 7 días · Préstamo 3: La Araucana, hoy, 7 días · Préstamo solapado: Don Quijote, hoy + 3 días, 7 días |
| Pasos | 1. Solicitar Don Quijote por 7 días y confirmar.<br>2. Solicitar Martín Fierro por 7 días y confirmar.<br>3. Intentar un tercer préstamo de La Araucana.<br>4. Intentar un préstamo de Don Quijote que comienza antes de su devolución.<br>5. Revisar "Mis reservas" y el cupo de préstamos. |
| Resultado esperado | El tercer préstamo se rechaza con el mensaje de límite de 2 préstamos activos. El préstamo solapado se rechaza porque el libro sigue prestado; "Mis reservas" conserva solo los dos primeros y el cupo muestra 2 de 2. |
| Resultado obtenido | Pendiente |
| Estado | Pendiente |
| Evidencia | `docs/week-03/evidence/CP-19.png` |
| Ejecutado por / fecha | Pendiente |

## CP-20 — Catálogo por bloque y “Solo disponibles”

| Campo | Detalle |
|---|---|
| Requisito asociado | RF-01 (CU1 Buscar recurso) |
| Tipo | Positivo |
| Precondiciones | Seed cargado. Sala 3 reservada en el bloque por defecto; Proyector Epson libre. Sesión como estudiante1@example.com. |
| Datos de entrada | Fecha y bloque del día · Luego “Solo disponibles” activado |
| Pasos | 1. Abrir "Buscar" y la pestaña "Salas y equipos".<br>2. Verificar que no hay resultados ni mensajes de error y que la vista pide elegir fecha y bloque.<br>3. Elegir la fecha y el bloque donde Sala 3 está reservada.<br>4. Confirmar que Sala 3 aparece como "Reservado" y sin botón de reserva.<br>5. Activar "Solo disponibles".<br>6. Verificar que Sala 3 desaparece y Proyector Epson se mantiene. |
| Resultado esperado | Al entrar no se muestran resultados ni errores: la vista pide elegir fecha y bloque. Con ambos elegidos se listan todos los recursos con su estado y “Solo disponibles” oculta los ocupados. |
| Resultado obtenido | Pendiente |
| Estado | Pendiente |
| Evidencia | `docs/week-03/evidence/CP-20.png` |
| Ejecutado por / fecha | Pendiente |

## CP-21 — Panel operativo del bibliotecario

| Campo | Detalle |
|---|---|
| Requisito asociado | RF-04, RF-05, RF-08 (CU4 Validar inicio, CU5 Registrar devolución) |
| Tipo | Positivo |
| Precondiciones | Seed cargado. Una reserva de bloque pendiente, un préstamo de libro activo y una sanción activa. Sesión como bibliotecario1@example.com. |
| Datos de entrada | Panel del día · pestañas · filtros por estado, bloque y búsqueda por código |
| Pasos | 1. Iniciar sesión como bibliotecario1@example.com.<br>2. Abrir "Panel" y verificar las cuatro pestañas: Operación, Inventario, Reservas del día y Validación.<br>3. En "Operación", revisar los KPIs: reservas, pendientes, en uso, préstamos, vencen hoy, vencidos, sanciones y canceladas.<br>4. Revisar "Próximas entregas", "Devoluciones de libros", "Sanciones activas" y la ocupación de los 13 bloques.<br>5. En "Reservas del día", filtrar por estado y por código; verificar que la pestaña se mantiene al filtrar.<br>6. En "Validación", buscar un código y verificar que la pestaña activa es la de validación.<br>7. Revisar que la barra superior no muestre el rol. |
| Resultado esperado | El panel agrupa sus secciones en cuatro pestañas y muestra solo la activa; los KPIs y la agenda usan datos reales; la ocupación refleja reservas y préstamos; los filtros acotan la tabla sin perder la pestaña; un código lleva a Validación; la barra superior muestra solo el nombre. |
| Resultado obtenido | Pendiente |
| Estado | Pendiente |
| Evidencia | `docs/week-03/evidence/CP-21.png` |
| Ejecutado por / fecha | Pendiente |

## CP-22 — Cancelación de una reserva por el solicitante

| Campo | Detalle |
|---|---|
| Requisito asociado | RF-02 (CU2 Reservar recurso) |
| Tipo | Positivo |
| Precondiciones | Seed cargado. Estudiante2 tiene una reserva pendiente en un bloque futuro. Sesión como estudiante2@example.com. |
| Datos de entrada | Reserva propia, bloque futuro, cupo diario con 1 de 2 usadas |
| Pasos | 1. Abrir "Mis reservas".<br>2. Verificar que la reserva activa muestra el botón "Cancelar reserva".<br>3. Presionar "Cancelar reserva" y confirmar en el diálogo.<br>4. Verificar que la reserva pasa al historial como "Cancelada" con su motivo.<br>5. Verificar que el cupo diario vuelve a 0 de 2.<br>6. Reservar de nuevo el mismo bloque para confirmar que quedó libre.<br>7. Abrir por URL el QR de la reserva cancelada. |
| Resultado esperado | La reserva queda Cancelada con quién, cuándo y motivo "Solicitud del usuario"; el bloque y el cupo se liberan; el QR anterior se rechaza con el mensaje de reserva cancelada. |
| Resultado obtenido | Pendiente |
| Estado | Pendiente |
| Evidencia | `docs/week-03/evidence/CP-22.png` |
| Ejecutado por / fecha | Pendiente |

## CP-23 — Límites de la cancelación

| Campo | Detalle |
|---|---|
| Requisito asociado | RF-02 (CU2 Reservar recurso) |
| Tipo | Negativo |
| Precondiciones | Una reserva de estudiante2, una reserva En Uso, una Finalizada y sesión de bibliotecario1. |
| Datos de entrada | Intentos de cancelación fuera de regla |
| Pasos | 1. Como estudiante1, abrir por URL `/mis-reservas/<id>/cancelar/` de una reserva de estudiante2.<br>2. Como bibliotecario, cancelar una reserva En Uso.<br>3. Cancelar una reserva Finalizada.<br>4. Cancelar desde la tabla sin elegir motivo.<br>5. Como solicitante, cancelar un bloque cuya hora ya comenzó. |
| Resultado esperado | El primer intento responde 404; los demás muestran un mensaje claro y ninguna reserva cambia de estado. Una reserva En Uso se resuelve con devolución, no con cancelación. |
| Resultado obtenido | Pendiente |
| Estado | Pendiente |
| Evidencia | `docs/week-03/evidence/CP-23.png` |
| Ejecutado por / fecha | Pendiente |

## CP-24 — Filtros vacíos y validación solo al enviar

| Campo | Detalle |
|---|---|
| Requisito asociado | RF-01 (CU1 Buscar recurso) |
| Tipo | Límite |
| Precondiciones | Seed cargado. Sesión como estudiante1@example.com. |
| Datos de entrada | Formulario sin filtros · Envío incompleto · URL con fecha y bloque |
| Pasos | 1. Abrir "Buscar" sin filtros.<br>2. Verificar que los campos de fecha y bloque están vacíos, que no hay errores y que la vista pide elegir.<br>3. Abrir el selector de bloque y verificar que solo ofrece "Elige un bloque".<br>4. Presionar "Filtrar" sin elegir nada.<br>5. Elegir una fecha y verificar que el bloque no queda autoseleccionado.<br>6. Abrir una URL con fecha y bloque ya definidos. |
| Resultado esperado | Entrar no dispara errores; los mensajes aparecen solo al enviar; el bloque nunca se autoselecciona; un enlace con fecha y bloque sigue mostrando resultados. |
| Resultado obtenido | Pendiente |
| Estado | Pendiente |
| Evidencia | `docs/week-03/evidence/CP-24.png` |
| Ejecutado por / fecha | Pendiente |

## CP-25 — Filtro del estado del inventario

| Campo | Detalle |
|---|---|
| Requisito asociado | RF-01, RF-04 (CU1 Buscar recurso, CU4 Validar inicio) |
| Tipo | Positivo |
| Precondiciones | Seed cargado. Sesión como bibliotecario1@example.com. |
| Datos de entrada | `inv_q=Sala` · `inv_tipo=EQUIPO` · `inv_estado=RESERVADO` · combinación sin resultados |
| Pasos | 1. Abrir el panel y la pestaña "Inventario".<br>2. Filtrar por nombre "Sala" y verificar el contador "Mostrando 2 de 10".<br>3. Filtrar por tipo "Equipo".<br>4. Filtrar por estado "Reservado".<br>5. Combinar filtros sin coincidencias y usar "Limpiar filtros".<br>6. Verificar que los contadores de arriba no cambian al filtrar. |
| Resultado esperado | La tabla se acota al filtro y el contador refleja cuántos de cuántos se ven; los totales del resumen siguen siendo globales; "Limpiar" vuelve a la pestaña Inventario sin filtros. |
| Resultado obtenido | Pendiente |
| Estado | Pendiente |
| Evidencia | `docs/week-03/evidence/CP-25.png` |
| Ejecutado por / fecha | Pendiente |

## CP-26 — Filtros reactivos

| Campo | Detalle |
|---|---|
| Requisito asociado | RF-01 (CU1 Buscar recurso) |
| Tipo | Positivo |
| Precondiciones | Seed cargado. Sesiones de estudiante1 y bibliotecario1. Navegador con y sin JavaScript. |
| Datos de entrada | Cambios en selectores y casillas de filtro |
| Pasos | 1. En "Buscar", elegir fecha y luego bloque: los resultados aparecen sin presionar "Filtrar".<br>2. Cambiar "Tipo de recurso" con fecha y bloque ya elegidos.<br>3. En el panel, cambiar el estado del filtro de reservas y el estado del inventario.<br>4. Escribir en "Título o autor" y verificar que no se envía sola.<br>5. Desactivar JavaScript y repetir un filtro con el botón "Filtrar". |
| Resultado esperado | Los selectores y casillas envían el formulario al cambiar; la búsqueda de texto no se autoenvía; con JavaScript desactivado el botón "Filtrar" sigue funcionando. |
| Resultado obtenido | Pendiente |
| Estado | Pendiente |
| Evidencia | `docs/week-03/evidence/CP-26.png` |
| Ejecutado por / fecha | Pendiente |

## (a) Distribución por tipo

Semana 2 (casos diseñados):

| Tipo | Cantidad | Casos |
|---|---|---|
| Positivo | 3 | CP-01, CP-02, CP-05 |
| Negativo | 1 | CP-04 |
| Límite | 2 | CP-03, CP-06 |
| Total | 6 |  |

Plan completo (14 casos, propuesta `[VERIFICAR]` para CP-07 a CP-12):

| Tipo | Cantidad | Casos |
|---|---|---|
| Positivo | 6 | CP-01, CP-02, CP-05, CP-09, CP-10, CP-13 |
| Negativo | 4 | CP-04, CP-07, CP-11, CP-14 |
| Límite | 4 | CP-03, CP-06, CP-08, CP-12 |
| Total | 14 | Cumple ≥ 3 negativos y ≥ 2 de límite |

Casos agregados en semana 3:

| Tipo | Cantidad | Casos |
|---|---|---|
| Positivo | 1 | CP-13 |
| Negativo | 1 | CP-14 |
| Límite | 0 | — |
| Total | 2 |  |

Casos agregados tras la revisión docente (MVP 1):

| Tipo | Cantidad | Casos |
|---|---|---|
| Positivo | 1 | CP-16 |
| Negativo | 1 | CP-15 |
| Límite | 0 | — |
| Total | 2 |  |

Casos agregados en la revisión del MVP 2 (ventana de reserva):

| Tipo | Cantidad | Casos |
|---|---|---|
| Positivo | 0 | — |
| Negativo | 0 | — |
| Límite | 1 | CP-17 |
| Total | 1 |  |

Casos agregados en la revisión del MVP 2 (libros):

| Tipo | Cantidad | Casos |
|---|---|---|
| Positivo | 1 | CP-18 |
| Negativo | 0 | — |
| Límite | 1 | CP-19 |
| Total | 2 |  |

Casos agregados en la revisión del MVP 2 (catálogo y horario):

| Tipo | Cantidad | Casos |
|---|---|---|
| Positivo | 1 | CP-20 |
| Negativo | 0 | — |
| Límite | 0 | — |
| Total | 1 |  |

Casos agregados en la revisión del panel (MVP 2):

| Tipo | Cantidad | Casos |
|---|---|---|
| Positivo | 1 | CP-21 |
| Negativo | 0 | — |
| Límite | 0 | — |
| Total | 1 |  |

Casos agregados en la corrección S3 (cancelación, filtros y pestañas):

| Tipo | Cantidad | Casos |
|---|---|---|
| Positivo | 3 | CP-22, CP-25, CP-26 |
| Negativo | 1 | CP-23 |
| Límite | 1 | CP-24 |
| Total | 5 | |

## (b) Plan original de CP-07 a CP-14

> Estos casos ya están desarrollados en la sección anterior; la tabla se conserva
> como registro del plan de la semana 2.

| ID | Caso (propuesto) | Tipo | Requisito | Semana | Evidencia propuesta |
|---|---|---|---|---|---|
| CP-07 | Login con credenciales ficticias inválidas rechazado; con credenciales válidas carga la vista según rol | Negativo | RF-08 | 3 | `docs/week-03/evidence/CP-07.png` |
| CP-11 | Búsqueda sin resultados muestra mensaje claro | Negativo | RF-01 | 3 | `docs/week-03/evidence/CP-11.png` |
| CP-12 | Devolución exactamente a las 11:00 (bloque hasta 11:00) no genera sanción | Límite | RF-07 | 3 | `docs/week-03/evidence/CP-12.png` |
| CP-13 | "Mis reservas" lista las reservas propias con su estado y reabre el QR | Positivo | RF-02, RF-03 | 3 | `docs/week-03/evidence/CP-13.png` |
| CP-14 | Un usuario no ve ni abre el QR de una reserva ajena | Negativo | RF-03, RF-08 | 3 | `docs/week-03/evidence/CP-14.png` |
| CP-08 | Reserva + QR en ≤ 1,5 s: promedio de 20 peticiones concurrentes con script/curl | Límite | RNF-01 | 4 | `docs/week-03/evidence/CP-08.txt` |
| CP-09 | Layout sin scroll horizontal ni textos cortados en 3 resoluciones (360 px, 1280 px y una intermedia [COMPLETAR]) y Lighthouse accesibilidad ≥ 90 | Positivo | RNF-02 | 4 | `docs/week-03/evidence/CP-09.png` |
| CP-10 | Contraseñas con hash; datos ficticios; credenciales excluidas por .gitignore | Positivo | RNF-03 | 4 | `docs/week-03/evidence/CP-10.md` |

Semana 2: CP-01 a CP-06 (6) · Semana 3: CP-07, CP-11, CP-12, CP-13, CP-14 (5) · Semana 4: CP-08, CP-09, CP-10 (3).

## (c) Checklist de aceptación

- Los 6 casos de semana 2 tienen todos los campos de la plantilla.
- Distribución de semana 2: 3 positivos, 1 negativo, 2 de límite.
- Los resultados reflejan la ejecución real: 11 casos aprobados con evidencia y el resto en "Pendiente".
- El plan de 14 casos (6 + 5 + 3) está declarado.
- Los IDs CP-01…CP-26 coinciden con matriz-trazabilidad.md.
- No hay evidencias, capturas ni resultados inventados.
- Datos ficticios coherentes (2026-11-10, estudiante1@example.com, bloques definidos).
- Textos de botones y mensajes coinciden con los mockups [SEM2-T1]; lo no definido está marcado [COMPLETAR]/[VERIFICAR].

## (d) Decision log

| # | Decisión | Motivo |
|---|---|---|
| 1 | Todo resultado, estado y fecha de ejecución en "Pendiente". | El código no existe; no se inventan ejecuciones. |
| 2 | Recursos, botones, mensajes e ID RSV-NNNN tomados de los mockups (Sala 3, Sala 1, "Confirmar reserva", etc.). | Pasos reproducibles y coherentes con el diseño del equipo. |
| 3 | Se mantienen los bloques de 60 min de la pauta (10:00–11:00, 11:00–12:00, 15:00–16:00) aunque los mockups muestran 09:00–10:30. | La pauta exige esos bloques y CP-06 depende del fin de bloque a las 11:00; la diferencia queda como [VERIFICAR]. |
| 4 | CP-04 agrupa QR inválido y duplicado en dos escenarios (A y B) dentro de un único caso. | Mantener el ID obligatorio y verificar que el estado no cambie en ambos. |
| 5 | CP-04 a CP-06 usan el flujo del bibliotecario de los mockups: ingresar/escanear QR → tarjeta → "Confirmar entrega" o "Registrar devolución". | Es el flujo definido en RF-04 y RF-05 y en la Vista Bibliotecario. |
| 6 | CP-06 intenta la reserva posterior en Sala 1 15:00–16:00. | Evita depender de Sala 3, que acaba de devolverse. |
| 7 | CP-07 a CP-12 se proponen con tipos para cumplir ≥ 3 negativos y ≥ 2 límites en el total. | La pauta exige esa distribución en los 12 casos; el detalle final se define en semanas 3 y 4. |
| 8 | CP-08 y CP-09 usan los métodos de verificación del equipo (20 peticiones concurrentes; 3 resoluciones en DevTools). | Coherencia con la definición de RNF-01 y RNF-02. |
| 9 | Los casos usan solo datos @example.com, no los datos de los mockups. | Los mockups muestran nombre y correo de apariencia real; RNF-03 exige cero datos reales. |
| 10 | No se agregan RF/RNF ni funcionalidades fuera de alcance. | Regla de trabajo del proyecto. |
| 11 | CP-08 se clasifica como Límite, no como Positivo. | Verifica el comportamiento en el borde del umbral de RNF-01 (≤ 1,5 s); se corrige por `OBS-LOCAL-01` de la revisión interna. |
| 12 | Se agregan CP-13 y CP-14 en semana 3 al implementar la pantalla "Mis reservas". | La pantalla ya figura en los mockups (pestaña "Mis Reservas") y CP-03 la usa; los casos cubren el listado propio y el aislamiento entre usuarios. |
| 13 | CP-13 y CP-14 quedan en "Pendiente" hasta ejecutarse con captura real. | No se marca un caso como Aprobado sin evidencia; el MVP ya permite ejecutarlos, pero falta la captura. |
| 14 | Se agregan CP-15 y CP-16 tras la revisión docente del MVP 1. | Cubren el rechazo de fechas pasadas y la visibilidad del inventario en el panel; responden a observaciones concretas del docente y quedan Pendiente hasta su ejecución con captura. |
| 15 | Se agrega CP-17 en la revisión del MVP 2. | Valida los tres bordes de la ventana de reserva: bloque iniciado, antelación de 15 minutos y horizonte de 7 días. |
| 16 | Se agrega CP-18 en la revisión del MVP 2. | Valida el catálogo de libros, la ficha bibliográfica y el préstamo con el mismo flujo de QR; queda Pendiente hasta su captura. |
| 17 | Se agrega CP-19 en la revisión del MVP 2. | Cubre los bordes del préstamo de libros: solapamiento y máximo de 2 préstamos activos. |
| 18 | Se agrega CP-20 en la revisión del MVP 2. | Cubre el catálogo inicial con estado, “Solo disponibles” y la validación solo al presionar Filtrar. |
| 19 | Se agrega CP-21 en la revisión del panel. | Cubre los KPIs, la agenda, la ocupación, las sanciones activas, los filtros y la ausencia del rol en la barra. |
| 20 | Se reescribe CP-20 en la corrección S3. | Los filtros inician vacíos, así que el catálogo ya no se muestra al entrar: primero se elige fecha y bloque. |
| 21 | Se agregan CP-22 y CP-23 para la cancelación. | Cubren la anulación por el solicitante y sus límites (reserva ajena, En Uso, Finalizada, sin motivo y bloque iniciado), dentro de RF-02. |
| 22 | Se agrega CP-24 para el estado inicial de los filtros. | Valida que no haya errores al entrar, que el bloque no se autoseleccione y que la validación ocurra solo al enviar. |
| 23 | Se agrega CP-25 para el filtro del inventario. | La tabla del inventario puede acotarse por nombre, tipo y estado sin alterar los contadores globales. |
| 24 | Se agrega CP-26 para los filtros reactivos. | Es manual: el proyecto no tiene runner de JavaScript, así que se verifica con el navegador con y sin JS. |
