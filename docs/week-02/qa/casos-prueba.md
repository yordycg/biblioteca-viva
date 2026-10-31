# Casos de prueba

> Semana 2 · Resultados `Pendiente` hasta que exista ejecución real.
> Datos ficticios; sin nombres, correos ni teléfonos reales.

## CP-01 — Búsqueda de recurso disponible

| Campo | Detalle |
|---|---|
| Requisito asociado | RF-01 |
| Tipo | Positivo |
| Precondiciones | Usuario autenticado; existe una sala libre para la fecha y bloque |
| Datos de entrada | Tipo: Sala; fecha: 2026-11-10; bloque: 10:00–11:00 |
| Pasos | 1. Ingresar a búsqueda. 2. Seleccionar tipo Sala. 3. Elegir fecha y bloque. 4. Presionar Buscar. |
| Resultado esperado | Se listan solo recursos libres para ese bloque; si no hay, aparece mensaje claro |
| Resultado obtenido | Pendiente |
| Estado | Pendiente |
| Evidencia | `docs/week-02/evidence/CP-01.png` |
| Ejecutado por / fecha | Pendiente |

## CP-02 — Reserva exitosa y generación de QR

| Campo | Detalle |
|---|---|
| Requisito asociado | RF-02, RF-03 |
| Tipo | Positivo |
| Precondiciones | Usuario autenticado; recurso libre; sin sanción; menos de 2 reservas activas ese día |
| Datos de entrada | Usuario: `estudiante1@example.com`; recurso: `Sala A`; fecha: 2026-11-10; bloque: 11:00–12:00 |
| Pasos | 1. Buscar el recurso. 2. Abrir detalle. 3. Confirmar reserva. |
| Resultado esperado | Reserva registrada; el bloque deja de estar disponible; se muestra un QR con el ID de reserva |
| Resultado obtenido | Pendiente |
| Estado | Pendiente |
| Evidencia | `docs/week-02/evidence/CP-02.png` |
| Ejecutado por / fecha | Pendiente |

## CP-03 — Tercera reserva del día rechazada

| Campo | Detalle |
|---|---|
| Requisito asociado | RF-06 |
| Tipo | Límite |
| Precondiciones | Usuario con 2 reservas activas para la misma fecha |
| Datos de entrada | Usuario: `estudiante1@example.com`; fecha: 2026-11-10; tercer bloque: 15:00–16:00 |
| Pasos | 1. Iniciar sesión. 2. Buscar un recurso libre para el tercer bloque. 3. Intentar reservar. |
| Resultado esperado | La reserva se rechaza con mensaje que explica el máximo de 2 reservas activas por día |
| Resultado obtenido | Pendiente |
| Estado | Pendiente |
| Evidencia | `docs/week-02/evidence/CP-03.png` |
| Ejecutado por / fecha | Pendiente |

## CP-04 — QR inválido o duplicado rechazado

| Campo | Detalle |
|---|---|
| Requisito asociado | RF-04 |
| Tipo | Negativo |
| Precondiciones | Bibliotecario autenticado; una reserva válida y una reserva ya utilizada |
| Datos de entrada | QR inválido: `NO-EXISTE`; QR duplicado: código de una reserva ya iniciada |
| Pasos | 1. Abrir vista bibliotecario. 2. Ingresar el QR inválido. 3. Intentar validar. 4. Repetir con el QR duplicado. |
| Resultado esperado | Ambos intentos se rechazan con mensaje claro; el estado de la reserva no cambia |
| Resultado obtenido | Pendiente |
| Estado | Pendiente |
| Evidencia | `docs/week-02/evidence/CP-04.png` |
| Ejecutado por / fecha | Pendiente |

## CP-05 — Devolución dentro de la hora

| Campo | Detalle |
|---|---|
| Requisito asociado | RF-05 |
| Tipo | Positivo |
| Precondiciones | Reserva en estado “En Uso”; devolución dentro del bloque |
| Datos de entrada | QR de la reserva; hora actual: 10:55; bloque: 10:00–11:00 |
| Pasos | 1. Abrir vista bibliotecario. 2. Escanear/ingresar el QR. 3. Registrar devolución. |
| Resultado esperado | La reserva pasa a “Finalizada” y el recurso vuelve a estar disponible |
| Resultado obtenido | Pendiente |
| Estado | Pendiente |
| Evidencia | `docs/week-02/evidence/CP-05.png` |
| Ejecutado por / fecha | Pendiente |

## CP-06 — Devolución 1 minuto después del bloque

| Campo | Detalle |
|---|---|
| Requisito asociado | RF-07 |
| Tipo | Límite |
| Precondiciones | Reserva en estado “En Uso”; devolución fuera del bloque |
| Datos de entrada | QR de la reserva; hora actual: 11:01; bloque: 10:00–11:00 |
| Pasos | 1. Abrir vista bibliotecario. 2. Escanear/ingresar el QR. 3. Registrar devolución. |
| Resultado esperado | La reserva finaliza; el usuario queda sancionado por 7 días y no puede reservar |
| Resultado obtenido | Pendiente |
| Estado | Pendiente |
| Evidencia | `docs/week-02/evidence/CP-06.png` |
| Ejecutado por / fecha | Pendiente |

## Distribución

| Tipo | Cantidad | Casos |
|---|---|---|
| Positivos | 3 | CP-01, CP-02, CP-05 |
| Negativos | 1 | CP-04 |
| Límite | 2 | CP-03, CP-06 |

> Semana 2 diseña 6 casos. La pauta pide 12 ejecutados en semana 4: se agregan 3 en semana 3 y 3 en semana 4.

## Plan de casos restantes

| Caso | Tipo | Requisito | Semana |
|---|---|---|---|
| CP-07 | Negativo | RF-08 | 3 |
| CP-08 | Límite | RNF-01 | 3 |
| CP-09 | Positivo | RNF-02 | 3 |
| CP-10 | Negativo | RNF-03 | 4 |
| CP-11 | Negativo | RF-01 | 4 |
| CP-12 | Límite | RF-07 | 4 |
