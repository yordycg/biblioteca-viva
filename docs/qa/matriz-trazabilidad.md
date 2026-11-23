# Matriz de trazabilidad — BibliotecaViva (diseño SEM2-T5, ejecución semana 3)

Estado real al 2026-11-20: los 27 casos están ejecutados y aprobados con evidencia. CP-26 falló el 2026-11-19 por DEF-03 y se cerró con la re-prueba del 2026-11-20 (paso 5 sin JavaScript). CP-27 se agregó en el cierre para dejar automatizado el flujo completo en navegador (Selenium).

La columna «Estado de implementación» refleja el código de la semana 3 y las correcciones de DEF-03, DEF-04, DEF-05 y la regeneración de capturas de DEF-06, respaldado por `python manage.py test` (91 pruebas automáticas al 2026-11-20), no por casos de prueba ejecutados. Las capturas de `evidence/rnf-02/` verifican el renderizado a 360 y 1280 px, y las auditorías de `evidence/rnf-02/lighthouse/` y `evidence/w3c/` son la evidencia de CP-09.

## Matriz principal

| ID Req | Funcionalidad | ID Prueba | Resultado | Evidencia | Estado de implementación |
|---|---|---|---|---|---|
| RF-01 | Búsqueda de recurso | CP-01, CP-11, CP-15, CP-17, CP-18, CP-20, CP-24, CP-25, CP-26 | Aprobado: los nueve casos con evidencia; CP-26 cerrado tras DEF-03 | `docs/evidence/CP-01.png`, `docs/evidence/CP-11.png`, `docs/evidence/CP-15.png`, `docs/evidence/CP-17.png`, `docs/evidence/CP-18.png`, `docs/evidence/CP-20.png`, `docs/evidence/CP-24.png`, `docs/evidence/CP-25.png`, `docs/evidence/CP-26.png`, `docs/evidence/CP-26-reprueba.png` | Implementado (listado inicial completo, catálogo por bloque, ventana de reserva, filtros opcionales y reactivos, formulario usable sin JavaScript) |
| RF-02 | Reserva de recurso | CP-02, CP-13, CP-15, CP-17, CP-18, CP-19, CP-22, CP-23 | Aprobado: CP-02, CP-13, CP-15, CP-17, CP-18, CP-19, CP-22, CP-23 con evidencia | `docs/evidence/CP-02.png`, `docs/evidence/CP-13.png`, `docs/evidence/CP-15.png`, `docs/evidence/CP-17.png`, `docs/evidence/CP-18.png`, `docs/evidence/CP-19.png`, `docs/evidence/CP-22.png`, `docs/evidence/CP-23.png` | Implementado (reserva por bloque, préstamo de libros y cancelación con auditoría) |
| RF-03 | Generación de comprobante (QR) | CP-02, CP-13, CP-14 | Aprobado: CP-02, CP-13, CP-14 con evidencia | `docs/evidence/CP-02.png`, `docs/evidence/CP-13.png`, `docs/evidence/CP-14.png` | Implementado (QR con ID de reserva) |
| RF-04 | Validación de entrega (check-in) | CP-04, CP-16, CP-21, CP-25 | Aprobado: CP-04, CP-16, CP-21, CP-25 con evidencia | `docs/evidence/CP-04.png`, `docs/evidence/CP-16.png`, `docs/evidence/CP-21.png`, `docs/evidence/CP-25.png` | Implementado (validación manual del código y panel con pestañas) |
| RF-05 | Registro de devolución (check-out) | CP-05, CP-16, CP-21 | Aprobado: CP-05, CP-16, CP-21 con evidencia | `docs/evidence/CP-05.png`, `docs/evidence/CP-16.png`, `docs/evidence/CP-21.png` | Implementado (devolución y liberación del recurso) |
| RF-06 | Control de tope de reservas | CP-03, CP-19 | Aprobado: CP-03, CP-19 con evidencia | `docs/evidence/CP-03.png`, `docs/evidence/CP-19.png` | Implementado (2 reservas y 2 préstamos activos) |
| RF-07 | Gestión de penalizaciones por retraso | CP-06, CP-12 | Aprobado: CP-06, CP-12 con evidencia | `docs/evidence/CP-06.png`, `docs/evidence/CP-12.png` | Implementado (sanción de 7 días) |
| RF-08 | Autenticación y roles básicos | CP-07, CP-14, CP-21 | Aprobado: CP-07, CP-14, CP-21 con evidencia | `docs/evidence/CP-07.png`, `docs/evidence/CP-14.png`, `docs/evidence/CP-21.png` | Implementado (login y roles) |
| RNF-01 | Rendimiento en reserva y QR | CP-08 | Aprobado: CP-08 con evidencia funcional y de carga | `docs/evidence/CP-08.txt`, `docs/evidence/rnf-01-estres/` | Implementado; medición de 20 reservas y carga con JMeter a 1, 10 y 50 usuarios |
| RNF-02 | Usabilidad y diseño responsivo | CP-09 | Aprobado: CP-09 con evidencia | `docs/evidence/CP-09.png`, `docs/evidence/rnf-02/`, `docs/evidence/rnf-02/lighthouse/`, `docs/evidence/w3c/` | Implementado (360, 768 y 1280 px); Lighthouse 100 en accesibilidad y 0 errores de marcado del W3C |
| RNF-03 | Seguridad de datos | CP-10 | Aprobado: CP-10 con evidencia | `docs/evidence/CP-10.png` | Implementado (PBKDF2, .env y base ignorados, sin datos reales) |

> **Caso transversal:** CP-27 recorre en un navegador real el flujo completo de
> RF-01 a RF-05 y RF-08 (login, búsqueda, reserva, QR, entrega y devolución). No
> se repite en cada fila para no inflar la matriz.

## (a) Casos de prueba CP-01 a CP-06 y CP-13 a CP-27

| ID Prueba | Tipo | Requisito | Caso de uso | Qué valida |
|---|---|---|---|---|
| CP-01 | Positivo | RF-01 | CU1 Buscar recurso | La búsqueda por tipo, fecha y bloque horario lista únicamente recursos libres. |
| CP-02 | Positivo | RF-02, RF-03 | CU2 Reservar recurso, CU3 Visualizar QR | La reserva se registra, el bloque deja de estar disponible y se muestra un QR con el ID de reserva decodificable. |
| CP-03 | Límite | RF-06 | CU2 Reservar recurso | La 3ª reserva del día se rechaza con mensaje del tope y las 2 anteriores quedan intactas. |
| CP-04 | Negativo | RF-04 | CU4 Validar inicio | Un QR inválido (NO-EXISTE) y uno duplicado se rechazan sin cambiar el estado de la reserva. |
| CP-05 | Positivo | RF-05 | CU5 Registrar devolución | La devolución dentro del bloque deja la reserva Finalizada y libera el recurso sin sanción. |
| CP-06 | Límite | RF-07 | CU5 Registrar devolución, CU6 Aplicar sanción | La devolución a las 11:01 (bloque hasta 11:00) finaliza la reserva, aplica 7 días de sanción y rechaza una reserva posterior. |
| CP-13 | Positivo | RF-02, RF-03 | CU2 Reservar recurso, CU3 Visualizar QR | "Mis reservas" muestra las reservas propias separadas en Activas/Historial y reabre el QR de una reserva activa. |
| CP-14 | Negativo | RF-03, RF-08 | CU3 Visualizar QR, CU0 Iniciar Sesión | Un usuario no ve en su lista ni puede abrir por URL el QR de una reserva ajena. |
| CP-15 | Negativo | RF-01, RF-02 | CU1 Buscar recurso, CU2 Reservar recurso | La búsqueda y la confirmación por URL forzada rechazan fechas anteriores al día actual sin crear reserva ni QR. |
| CP-16 | Positivo | RF-04, RF-05 | CU4 Validar inicio, CU5 Registrar devolución | El panel muestra por recurso y bloque cuántos están disponibles, reservados, en uso o no disponibles, y actualiza los contadores tras una devolución. |
| CP-17 | Límite | RF-01, RF-02 | CU1 Buscar recurso, CU2 Reservar recurso | Hoy solo se ofrecen bloques con 15 minutos de antelación; el servidor rechaza bloques iniciados y fechas fuera del horizonte de 7 días. |
| CP-18 | Positivo | RF-01, RF-02 | CU1 Buscar recurso, CU2 Reservar recurso | El catálogo filtra libros, la ficha muestra carátula y datos bibliográficos, y el préstamo genera su QR y descuenta el cupo. |
| CP-19 | Límite | RF-02, RF-06 | CU2 Reservar recurso | Un libro no se puede prestar si su rango se solapa con un préstamo activo, y un usuario no puede superar 2 préstamos activos. |
| CP-20 | Positivo | RF-01 | CU1 Buscar recurso | Al entrar no hay resultados ni errores; con fecha y bloque se listan todos los recursos con su estado y “Solo disponibles” oculta los ocupados. |
| CP-21 | Positivo | RF-04, RF-05, RF-08 | CU4, CU5 | El panel agrupa sus secciones en cuatro pestañas, conserva la pestaña al filtrar y muestra KPIs, agenda, ocupación y sanciones; la barra superior no muestra el rol. |
| CP-22 | Positivo | RF-02 | CU2 Reservar recurso | El solicitante cancela su reserva pendiente: queda Cancelada con motivo y auditoría, libera bloque y cupo, y el QR anterior se rechaza. |
| CP-23 | Negativo | RF-02 | CU2 Reservar recurso | No se cancela una reserva ajena, ni una En Uso o Finalizada, ni sin motivo; ninguna cambia de estado. |
| CP-24 | Límite | RF-01 | CU1 Buscar recurso | El listado inicial muestra el catálogo completo, los filtros inician vacíos y la validación ocurre solo al enviar. |
| CP-25 | Positivo | RF-01, RF-04 | CU1 Buscar recurso, CU4 Validar inicio | El inventario se acota por nombre, tipo y estado sin alterar los contadores globales. |
| CP-26 | Positivo | RF-01 | CU1 Buscar recurso | Los selectores y casillas filtran al cambiar; sin JavaScript el botón Filtrar sigue funcionando y el texto no se autoenvía. |
| CP-27 | Positivo | RF-01 a RF-05, RF-08 | CU0 a CU5 | El flujo completo (login, búsqueda, reserva, QR, entrega y devolución) se ejecuta sin intervención manual en un navegador real. |

## (b) Plan de CP-07 a CP-12

| ID Prueba | Caso (propuesto) | Tipo | Requisito | Caso de uso | Semana | Estado |
|---|---|---|---|---|---|---|
| CP-07 | Login inválido rechazado; credenciales válidas cargan la vista según rol | Negativo | RF-08 | CU0 Iniciar Sesión | 3 | Aprobado |
| CP-11 | Búsqueda sin resultados muestra mensaje claro | Negativo | RF-01 | CU1 Buscar recurso | 3 | Aprobado |
| CP-12 | Devolución exactamente a las 11:00 no genera sanción | Límite | RF-07 | CU5 Registrar devolución | 3 | Aprobado |
| CP-13 | "Mis reservas" lista las reservas propias y reabre el QR | Positivo | RF-02, RF-03 | CU2, CU3 | 3 | Aprobado |
| CP-14 | Un usuario no ve ni abre el QR de una reserva ajena | Negativo | RF-03, RF-08 | CU3, CU0 | 3 | Aprobado |
| CP-08 | Reserva + QR en ≤ 1,5 s (promedio de 20 peticiones concurrentes) | Límite | RNF-01 | CU2, CU3 | 4 | Aprobado |
| CP-09 | Layout sin scroll horizontal en 3 resoluciones y Lighthouse accesibilidad ≥ 90 | Positivo | RNF-02 | Transversal | 4 | Aprobado |
| CP-10 | Contraseñas con hash; datos ficticios; .gitignore | Positivo | RNF-03 | CU0 Iniciar Sesión | 4 | Aprobado |

## Cómo mantener la matriz

- Enlazar cada caso nuevo a su requisito. Todo CP nuevo debe aparecer en ID Prueba de al menos un requisito, y viceversa.
- Cambiar "Resultado" solo con evidencia real. Pasar de Pendiente a otro valor exige el archivo de evidencia existente en `docs/evidence/` y el registro de quién ejecutó y cuándo en `casos-prueba.md`.
- La columna «Estado de implementación» describe el código, no la calidad verificada: "Implementado" no equivale a "Aprobado".
- Declarar explícitamente lo no implementado. Mientras un requisito no tenga código, su estado debe decir "No implementado (semana N)"; no dejar celdas vacías.
- Los defectos hallados al ejecutar se registran en `qa/defectos.md` con `DEF-XX` y se enlazan desde la ficha del caso. Un caso con defecto queda "Fallido" hasta su re-prueba.
- Actualizar la matriz en el PR de la semana correspondiente. Cada PR que implemente o pruebe un requisito actualiza la matriz y `casos-prueba.md` en el mismo cambio.

## Checklist de aceptación

- Los 11 requisitos (RF-01 a RF-08, RNF-01 a RNF-03) están presentes, cada uno con al menos un ID de prueba.
- Los resultados distinguen lo ejecutado (26 aprobados con evidencia, incluido el cierre de DEF-03 con su re-prueba) de lo no ejecutado.
- El estado de implementación es explícito en las 11 filas.
- IDs, tipos y requisitos son coherentes con casos-prueba.md (CP-01 a CP-26).
- Solo los requisitos con todos sus CP aprobados figuran como «Aprobado»; el resto queda «Parcial» o «Pendiente».
- Las rutas de evidencia usan .png para pantallas y .txt/.md para mediciones y logs (CP-08, CP-10).
- Los casos de uso citados coinciden con el diagrama (CU0–CU6).

## Decision log

| # | Decisión | Motivo |
|---|---|---|
| 1 | Resultado "Pendiente" en las 11 filas. | No hay ejecución ni evidencia real. |
| 2 | Nombres de requisitos tomados de la definición oficial del equipo. | Coherencia con la documentación de semana 1. |
| 3 | RF-02 y RF-03 comparten CP-02 (y su evidencia). | El caso valida reserva y QR en un mismo flujo, según el reparto indicado. |
| 4 | RF-01 y RF-07 tienen dos casos (CP-11 y CP-12 respectivamente). | Cubren el negativo de búsqueda sin resultados y el límite de devolución exacta a las 11:00. |
| 5 | Se agrega la columna "Caso de uso" solo en las tablas auxiliares; la matriz principal mantiene sus 6 columnas. | La pauta fija las columnas de la tabla principal; el vínculo con el diagrama de CU queda documentado. |
| 6 | Estado de implementación: RF implementados en semana 3; RNF-01 y RNF-03 con medición formal en semana 4. | Calendario del proyecto: F1–F3 en semana 3; medición de RNF en semana 4. |
| 7 | Tipos de CP-07 a CP-12 propuestos para completar la distribución del plan. | Detalle confirmado en semanas 3 y 4. |
| 8 | Rutas de evidencia definidas por caso; las de los CP pendientes son propuestas. | Los archivos se crean al ejecutar las pruebas; las rutas de los pendientes quedan reservadas. |
| 9 | CP-13 y CP-14 se agregan en semana 3 (pantalla "Mis reservas"). | La pantalla figura en los mockups y CP-03 la referencia; se enlazan a RF-02/RF-03 y RF-03/RF-08 y siguen en Pendiente hasta su ejecución. |
| 10 | «Estado de implementación» pasa de «No implementado» a «Implementado» en semana 3. | Lo respalda el código de F1–F3 y la suite automática (90 pruebas al cierre de S3); ningún CP se marca aprobado hasta su ejecución con evidencia. |
| 11 | Se agregan capturas de `evidence/rnf-02/` (360 y 1280 px). | Verifican el renderizado real de la interfaz; no reemplazan la ejecución de CP-09 ni la medición Lighthouse. |
| 12 | Se agregan CP-15 y CP-16 tras la revisión docente del MVP 1. | Responden a las observaciones sobre fechas pasadas y visibilidad del inventario; se enlazan a RF-01/RF-02 y RF-04/RF-05 y siguen Pendiente hasta su ejecución con captura. |
| 13 | Se agrega CP-17 en la revisión del MVP 2. | Cubre los bordes de la ventana de reserva (bloque iniciado, 15 minutos de antelación y 7 días de horizonte) sin agregar requisitos nuevos. |
| 14 | Se agrega CP-18 en la revisión del MVP 2. | Cubre el catálogo y el préstamo de libros; la funcionalidad se mantiene dentro de RF-01 y RF-02. |
| 15 | Se agrega CP-19 en la revisión del MVP 2. | Cubre el solapamiento de préstamos y el límite de 2 activos, enlazado a RF-02 y RF-06. |
| 16 | Se agrega CP-20 y se amplía el horario a 09:00–22:00. | El catálogo inicial, “Solo disponibles” y los 13 bloques responden a la revisión docente; se actualizan RF-01 y la matriz. |
| 17 | Se agrega CP-21 en la revisión del panel. | Valida los indicadores operativos, filtros y la ausencia del rol en la barra; enlazado a RF-04, RF-05 y RF-08. |
| 18 | Se agregan CP-22 y CP-23 en la corrección S3. | Cubren la cancelación por el solicitante y sus límites; se enlazan a RF-02 sin crear requisitos nuevos. |
| 19 | Se agregan CP-24, CP-25 y CP-26 en la corrección S3. | Cubren el estado inicial de los filtros, el filtro del inventario y los filtros reactivos; se enlazan a RF-01 y RF-04. |
| 20 | Se reescribe CP-20 y se amplía CP-21. | Los filtros inician vacíos (ya no hay catálogo al entrar) y el panel pasó a cuatro pestañas. |
| 21 | CP-01 se actualiza al RF-01 vigente y DEF-01 se cierra como defecto del caso. | RF-01 cambió en S3: el catálogo muestra todos los recursos con su estado y permite «Solo disponibles». La aplicación cumple el RF vigente; el caso conservaba el criterio de semana 2. |
| 22 | La suite automática pasa de 69 a 90 pruebas con la corrección S3 (PR #11). | El dato de 69 correspondía al 2026-11-12; el informe SEM-03 debe actualizarse a 90 al cierre de S3. |
| 23 | CP-26 se ejecuta el 2026-11-19 y RF-01 queda «Parcial» por DEF-03. | El caso estaba pendiente porque exige navegador con y sin JavaScript. Falló el paso 5 en «Salas y equipos»; el requisito no se marca aprobado hasta corregir DEF-03 y re-ejecutar el caso. |
| 24 | RF-01 pasa a «Aprobado» el 2026-11-20 al cerrar DEF-03. | La corrección de `BusquedaForm` permite enviar el formulario sin JavaScript; la re-prueba del paso 5 de CP-26 quedó con evidencia en `CP-26-reprueba.png`. |
