# Matriz de trazabilidad

> Semana 2 · Estado de los resultados: `Pendiente` hasta que exista evidencia de ejecución.
> Los requisitos no implementados se declaran explícitamente.

## Matriz

| ID Req | Funcionalidad | ID Prueba | Resultado | Evidencia | Estado de implementación |
|---|---|---|---|---|---|
| RF-01 | Búsqueda de recursos disponibles | CP-01, CP-11 | Pendiente | `docs/week-02/evidence/CP-01.png`, `CP-11.png` | No implementado (semana 3) |
| RF-02 | Reserva de recurso | CP-02 | Pendiente | `docs/week-02/evidence/CP-02.png` | No implementado (semana 3) |
| RF-03 | Generación de QR | CP-02 | Pendiente | `docs/week-02/evidence/CP-02.png` | No implementado (semana 3) |
| RF-04 | Validación de inicio | CP-04 | Pendiente | `docs/week-02/evidence/CP-04.png` | No implementado (semana 3) |
| RF-05 | Registro de devolución | CP-05 | Pendiente | `docs/week-02/evidence/CP-05.png` | No implementado (semana 3) |
| RF-06 | Máximo 2 reservas activas por día | CP-03 | Pendiente | `docs/week-02/evidence/CP-03.png` | No implementado (semana 3) |
| RF-07 | Sanción por devolución tardía | CP-06, CP-12 | Pendiente | `docs/week-02/evidence/CP-06.png`, `CP-12.png` | No implementado (semana 3) |
| RF-08 | Autenticación y roles | CP-07 | Pendiente | `docs/week-02/evidence/CP-07.png` | No implementado (semana 3) |
| RNF-01 | Rendimiento de reserva + QR | CP-08 | Pendiente | `docs/week-02/evidence/CP-08.txt` | No implementado (semana 4) |
| RNF-02 | Usabilidad responsiva | CP-09 | Pendiente | `docs/week-02/evidence/CP-09.png` | No implementado (semana 4) |
| RNF-03 | Seguridad de datos | CP-10 | Pendiente | `docs/week-02/evidence/CP-10.md` | No implementado (semana 4) |

## Casos diseñados en semana 2

| Caso | Tipo | Requisito | Qué valida |
|---|---|---|---|
| CP-01 | Positivo | RF-01 | Búsqueda devuelve solo recursos libres y mensaje claro si no hay |
| CP-02 | Positivo | RF-02, RF-03 | Reserva registrada y QR único generado |
| CP-03 | Límite | RF-06 | Tercera reserva del día rechazada |
| CP-04 | Negativo | RF-04 | QR inválido o duplicado rechazado |
| CP-05 | Positivo | RF-05 | Devolución dentro de hora finaliza y libera |
| CP-06 | Límite | RF-07 | Devolución 1 minuto tarde aplica sanción de 7 días |

> Los casos CP-07 a CP-12 se diseñan en semanas 3–4. No se inventan resultados: todo queda `Pendiente` hasta ejecutar.

## Plan de casos restantes

| Caso | Tipo | Requisito | Semana |
|---|---|---|---|
| CP-07 | Negativo | RF-08 | 3 |
| CP-08 | Límite | RNF-01 | 3 |
| CP-09 | Positivo | RNF-02 | 3 |
| CP-10 | Negativo | RNF-03 | 4 |
| CP-11 | Negativo | RF-01 | 4 |
| CP-12 | Límite | RF-07 | 4 |
