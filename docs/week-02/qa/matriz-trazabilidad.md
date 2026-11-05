# Matriz de trazabilidad — BibliotecaViva (Semana 2, SEM2-T5)

Estado real: el código de la aplicación aún no existe (F1–F3 parte en semana 3). Todos los resultados están en Pendiente; ningún requisito está aprobado ni implementado. Las rutas de evidencia son propuestas, no archivos existentes.

## Matriz principal

| ID Req | Funcionalidad | ID Prueba | Resultado | Evidencia | Estado de implementación |
|---|---|---|---|---|---|
| RF-01 | Búsqueda de recurso | CP-01, CP-11 | Pendiente | `docs/week-02/evidence/CP-01.png`, `docs/week-02/evidence/CP-11.png` | No implementado (semana 3) |
| RF-02 | Reserva de recurso | CP-02 | Pendiente | `docs/week-02/evidence/CP-02.png` | No implementado (semana 3) |
| RF-03 | Generación de comprobante (QR) | CP-02 | Pendiente | `docs/week-02/evidence/CP-02.png` | No implementado (semana 3) |
| RF-04 | Validación de entrega (check-in) | CP-04 | Pendiente | `docs/week-02/evidence/CP-04.png` | No implementado (semana 3) |
| RF-05 | Registro de devolución (check-out) | CP-05 | Pendiente | `docs/week-02/evidence/CP-05.png` | No implementado (semana 3) |
| RF-06 | Control de tope de reservas | CP-03 | Pendiente | `docs/week-02/evidence/CP-03.png` | No implementado (semana 3) |
| RF-07 | Gestión de penalizaciones por retraso | CP-06, CP-12 | Pendiente | `docs/week-02/evidence/CP-06.png`, `docs/week-02/evidence/CP-12.png` | No implementado (semana 3) |
| RF-08 | Autenticación y roles básicos | CP-07 | Pendiente | `docs/week-02/evidence/CP-07.png` | No implementado (semana 3) |
| RNF-01 | Rendimiento en reserva y QR | CP-08 | Pendiente | `docs/week-02/evidence/CP-08.txt` | No implementado (semana 4) |
| RNF-02 | Usabilidad y diseño responsivo | CP-09 | Pendiente | `docs/week-02/evidence/CP-09.png` | No implementado (semana 4) |
| RNF-03 | Seguridad de datos | CP-10 | Pendiente | `docs/week-02/evidence/CP-10.md` | No implementado (semana 4) |

## (a) Casos diseñados en semana 2

| ID Prueba | Tipo | Requisito | Caso de uso | Qué valida |
|---|---|---|---|---|
| CP-01 | Positivo | RF-01 | CU1 Buscar recurso | La búsqueda por tipo, fecha y bloque horario lista únicamente recursos libres. |
| CP-02 | Positivo | RF-02, RF-03 | CU2 Reservar recurso, CU3 Visualizar QR | La reserva se registra, el bloque deja de estar disponible y se muestra un QR con el ID de reserva decodificable. |
| CP-03 | Límite | RF-06 | CU2 Reservar recurso | La 3ª reserva del día se rechaza con mensaje del tope y las 2 anteriores quedan intactas. |
| CP-04 | Negativo | RF-04 | CU4 Validar inicio | Un QR inválido (NO-EXISTE) y uno duplicado se rechazan sin cambiar el estado de la reserva. |
| CP-05 | Positivo | RF-05 | CU5 Registrar devolución | La devolución dentro del bloque deja la reserva Finalizada y libera el recurso sin sanción. |
| CP-06 | Límite | RF-07 | CU5 Registrar devolución, CU6 Aplicar sanción | La devolución a las 11:01 (bloque hasta 11:00) finaliza la reserva, aplica 7 días de sanción y rechaza una reserva posterior. |

## (b) Plan de CP-07 a CP-12

| ID Prueba | Caso (propuesto) | Tipo | Requisito | Caso de uso | Semana |
|---|---|---|---|---|---|
| CP-07 | Login inválido rechazado; credenciales válidas cargan la vista según rol | Negativo | RF-08 | CU0 Iniciar Sesión | 3 |
| CP-11 | Búsqueda sin resultados muestra mensaje claro | Negativo | RF-01 | CU1 Buscar recurso | 3 |
| CP-12 | Devolución exactamente a las 11:00 no genera sanción | Límite | RF-07 | CU5 Registrar devolución | 3 |
| CP-08 | Reserva + QR en ≤ 1,5 s (promedio de 20 peticiones concurrentes) | Límite | RNF-01 | CU2, CU3 | 4 |
| CP-09 | Layout sin scroll horizontal en 3 resoluciones y Lighthouse accesibilidad ≥ 90 | Positivo | RNF-02 | Transversal | 4 |
| CP-10 | Contraseñas con hash; datos ficticios; .gitignore | Positivo | RNF-03 | CU0 Iniciar Sesión | 4 |

## Cómo mantener la matriz

- Enlazar cada caso nuevo a su requisito. Todo CP nuevo debe aparecer en ID Prueba de al menos un requisito, y viceversa.
- Cambiar "Resultado" solo con evidencia real. Pasar de Pendiente a otro valor exige el archivo de evidencia existente en docs/week-02/evidence/ y el registro de quién ejecutó y cuándo en casos-prueba.md.
- Declarar explícitamente lo no implementado. Mientras un requisito no tenga código, su estado debe decir "No implementado (semana N)"; no dejar celdas vacías.
- Actualizar la matriz en el PR de la semana correspondiente. Cada PR (rama feature/, con aprobación previa al merge, según el Plan de Calidad) que implemente o pruebe un requisito actualiza la matriz y casos-prueba.md en el mismo cambio.

## Checklist de aceptación

- Los 11 requisitos (RF-01 a RF-08, RNF-01 a RNF-03) están presentes, cada uno con al menos un ID de prueba.
- Todos los resultados están en "Pendiente".
- El estado de implementación es explícito en las 11 filas.
- IDs, tipos y requisitos son coherentes con casos-prueba.md (CP-01 a CP-06).
- Ningún requisito figura como aprobado o implementado sin evidencia.
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
| 6 | Estado de implementación: semana 3 para RF y semana 4 para RNF. | Calendario del proyecto: F1–F3 en semana 3; medición de RNF en semana 4. |
| 7 | Tipos de CP-07 a CP-12 propuestos para completar la distribución del plan. | Detalle final a confirmar al diseñarlos en semanas 3 y 4 [VERIFICAR]. |
| 8 | Rutas de evidencia son propuestas. | Los archivos se crearán solo al ejecutar las pruebas. |
