# Matriz de trazabilidad — BibliotecaViva (diseño SEM2-T5, ejecución semana 3)

Estado real: CP-01 a CP-12 se diseñaron en semana 2, antes de que existiera el código de F1–F3. CP-13 y CP-14 se agregaron en semana 3 al implementar la pantalla "Mis reservas" y CP-15 y CP-16 en la revisión docente del MVP 1. Todos los resultados están en Pendiente; ningún requisito está aprobado ni tiene evidencia ejecutada de CP. Las rutas de evidencia de CP son propuestas hasta que QA las genere.

La columna «Estado de implementación» refleja el código de la semana 3, respaldado por `python manage.py test` (26 pruebas automáticas), no por casos de prueba ejecutados. Las capturas de `evidence/rnf-02/` verifican el renderizado a 360 y 1280 px, pero no sustituyen la ejecución de CP-09.

## Matriz principal

| ID Req | Funcionalidad | ID Prueba | Resultado | Evidencia | Estado de implementación |
|---|---|---|---|---|---|
| RF-01 | Búsqueda de recurso | CP-01, CP-11, CP-15 | Pendiente | `docs/week-03/evidence/CP-01.png`, `docs/week-03/evidence/CP-11.png`, `docs/week-03/evidence/CP-15.png` | Implementado (búsqueda y filtros); CP pendiente |
| RF-02 | Reserva de recurso | CP-02, CP-13, CP-15 | Pendiente | `docs/week-03/evidence/CP-02.png`, `docs/week-03/evidence/CP-13.png`, `docs/week-03/evidence/CP-15.png` | Implementado; CP pendiente |
| RF-03 | Generación de comprobante (QR) | CP-02, CP-13, CP-14 | Pendiente | `docs/week-03/evidence/CP-02.png`, `docs/week-03/evidence/CP-13.png`, `docs/week-03/evidence/CP-14.png` | Implementado (QR con ID de reserva); CP pendiente |
| RF-04 | Validación de entrega (check-in) | CP-04, CP-16 | Pendiente | `docs/week-03/evidence/CP-04.png`, `docs/week-03/evidence/CP-16.png` | Implementado (validación manual del código); CP pendiente |
| RF-05 | Registro de devolución (check-out) | CP-05, CP-16 | Pendiente | `docs/week-03/evidence/CP-05.png`, `docs/week-03/evidence/CP-16.png` | Implementado; CP pendiente |
| RF-06 | Control de tope de reservas | CP-03 | Pendiente | `docs/week-03/evidence/CP-03.png` | Implementado; CP pendiente |
| RF-07 | Gestión de penalizaciones por retraso | CP-06, CP-12 | Pendiente | `docs/week-03/evidence/CP-06.png`, `docs/week-03/evidence/CP-12.png` | Implementado (sanción de 7 días); CP pendiente |
| RF-08 | Autenticación y roles básicos | CP-07, CP-14 | Pendiente | `docs/week-03/evidence/CP-07.png`, `docs/week-03/evidence/CP-14.png` | Implementado (login y roles); CP pendiente |
| RNF-01 | Rendimiento en reserva y QR | CP-08 | Pendiente | `docs/week-03/evidence/CP-08.txt` | Implementado; medición HTTP formal pendiente (S4) |
| RNF-02 | Usabilidad y diseño responsivo | CP-09 | Pendiente | `docs/week-03/evidence/CP-09.png`, `docs/week-03/evidence/rnf-02/` | Implementado (interfaz 360–1280 px); Lighthouse pendiente |
| RNF-03 | Seguridad de datos | CP-10 | Pendiente | `docs/week-03/evidence/CP-10.md` | Parcial: hash PBKDF2 y `.gitignore` verificados; auditoría formal pendiente |

## (a) Casos diseñados en semana 2

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

## (b) Plan de CP-07 a CP-12

| ID Prueba | Caso (propuesto) | Tipo | Requisito | Caso de uso | Semana |
|---|---|---|---|---|---|
| CP-07 | Login inválido rechazado; credenciales válidas cargan la vista según rol | Negativo | RF-08 | CU0 Iniciar Sesión | 3 |
| CP-11 | Búsqueda sin resultados muestra mensaje claro | Negativo | RF-01 | CU1 Buscar recurso | 3 |
| CP-12 | Devolución exactamente a las 11:00 no genera sanción | Límite | RF-07 | CU5 Registrar devolución | 3 |
| CP-13 | "Mis reservas" lista las reservas propias y reabre el QR | Positivo | RF-02, RF-03 | CU2, CU3 | 3 |
| CP-14 | Un usuario no ve ni abre el QR de una reserva ajena | Negativo | RF-03, RF-08 | CU3, CU0 | 3 |
| CP-08 | Reserva + QR en ≤ 1,5 s (promedio de 20 peticiones concurrentes) | Límite | RNF-01 | CU2, CU3 | 4 |
| CP-09 | Layout sin scroll horizontal en 3 resoluciones y Lighthouse accesibilidad ≥ 90 | Positivo | RNF-02 | Transversal | 4 |
| CP-10 | Contraseñas con hash; datos ficticios; .gitignore | Positivo | RNF-03 | CU0 Iniciar Sesión | 4 |

## Cómo mantener la matriz

- Enlazar cada caso nuevo a su requisito. Todo CP nuevo debe aparecer en ID Prueba de al menos un requisito, y viceversa.
- Cambiar "Resultado" solo con evidencia real. Pasar de Pendiente a otro valor exige el archivo de evidencia existente en `docs/week-03/evidence/` y el registro de quién ejecutó y cuándo en `casos-prueba.md`.
- La columna «Estado de implementación» describe el código, no la calidad verificada: "Implementado" no equivale a "Aprobado".
- Declarar explícitamente lo no implementado. Mientras un requisito no tenga código, su estado debe decir "No implementado (semana N)"; no dejar celdas vacías.
- Los defectos hallados al ejecutar se registran en `qa/defectos.md` con `DEF-XX` y se enlazan desde la ficha del caso. Un caso con defecto queda "Fallido" hasta su re-prueba.
- Actualizar la matriz en el PR de la semana correspondiente. Cada PR que implemente o pruebe un requisito actualiza la matriz y `casos-prueba.md` en el mismo cambio.

## Checklist de aceptación

- Los 11 requisitos (RF-01 a RF-08, RNF-01 a RNF-03) están presentes, cada uno con al menos un ID de prueba.
- Todos los resultados de CP están en "Pendiente".
- El estado de implementación es explícito en las 11 filas.
- IDs, tipos y requisitos son coherentes con casos-prueba.md (CP-01 a CP-16).
- Ningún requisito figura como aprobado: la implementación se respalda en código y pruebas automáticas, no en CP ejecutados.
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
| 7 | Tipos de CP-07 a CP-12 propuestos para completar la distribución del plan. | Detalle final a confirmar al diseñarlos en semanas 3 y 4 [VERIFICAR]. |
| 8 | Rutas de evidencia son propuestas. | Los archivos se crearán solo al ejecutar las pruebas. |
| 9 | CP-13 y CP-14 se agregan en semana 3 (pantalla "Mis reservas"). | La pantalla figura en los mockups y CP-03 la referencia; se enlazan a RF-02/RF-03 y RF-03/RF-08 y siguen en Pendiente hasta su ejecución. |
| 10 | «Estado de implementación» pasa de «No implementado» a «Implementado» en semana 3. | Lo respalda el código de F1–F3 y 13 pruebas automáticas; ningún CP se marca aprobado hasta su ejecución con evidencia. |
| 11 | Se agregan capturas de `evidence/rnf-02/` (360 y 1280 px). | Verifican el renderizado real de la interfaz; no reemplazan la ejecución de CP-09 ni la medición Lighthouse. |
| 12 | Se agregan CP-15 y CP-16 tras la revisión docente del MVP 1. | Responden a las observaciones sobre fechas pasadas y visibilidad del inventario; se enlazan a RF-01/RF-02 y RF-04/RF-05 y siguen Pendiente hasta su ejecución con captura. |
