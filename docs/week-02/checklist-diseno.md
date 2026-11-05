# Checklist de diseño — Semana 2

> **SEM2-T4** · Responsable: Yordy Carmona · Semana 2 · Evidencia: este archivo.
>
> Aplicar a requisitos, mockups y UML. Registrar cada hallazgo con fecha y responsable. No marcar “Cumple” sin evidencia.
>
> Aplicado el 2026-11-04 sobre los artefactos integrados en `week/sem2`: requisitos (`docs/week-01/02-requisitos.md`), mockups (`docs/week-02/mockups/`) y casos de uso (`docs/week-02/diagrams/casos-de-uso.mmd`). **Segunda pasada el 2026-11-05** sobre los artefactos integrados desde Drive: secuencia y clases (T3), casos de prueba (T6) y matriz de trazabilidad (T5). Queda `Pendiente` solo lo que depende de la ejecución de pruebas (semanas 3–4).

## 1. Requisitos

| Criterio | RF-01 | RF-02 | RF-03 | RF-04 | RF-05 | RF-06 | RF-07 | RF-08 | Observación |
|---|---|---|---|---|---|---|---|---|---|
| ID único | Cumple | Cumple | Cumple | Cumple | Cumple | Cumple | Cumple | Cumple | RF-01 a RF-08 sin duplicados |
| Atómico (una sola función) | Cumple | Cumple | Cumple | Cumple | Cumple | Cumple | Cumple | Cumple | |
| Medible / verificable | Cumple | Cumple | Cumple | Cumple | Cumple | Cumple | Cumple | Cumple | Todos con criterio Dado/Cuando/Entonces |
| Sin ambigüedad | Cumple | Cumple | Cumple | Cumple | Cumple | Parcial | Parcial | Cumple | RF-06 no define si una reserva cancelada libera cupo; RF-07 no fija tolerancia para “fuera de hora” [VERIFICAR] |
| Criterio de aceptación | Cumple | Cumple | Cumple | Cumple | Cumple | Cumple | Cumple | Cumple | |
| Pantalla asociada | Cumple | Cumple | Cumple | Cumple | Cumple | Cumple | Cumple | Pendiente | RF-01 lámina 1; RF-02/03/06 lámina 2; RF-04/05/07 lámina 3. RF-08 no tiene pantalla: el login no se entregó |
| UML consistente | Cumple | Cumple | Cumple | Cumple | Cumple | Parcial | Cumple | Cumple | RF-06 no tiene caso de uso propio: se aplica como regla dentro de CU2. T3 integrado el 2026-11-05; fuentes `.mmd` reconstruidas desde los PNG |

## 2. Requisitos no funcionales

| Criterio | RNF-01 | RNF-02 | RNF-03 | Observación |
|---|---|---|---|---|
| Métrica y umbral | Cumple | Cumple | Cumple | ≤ 1,5 s · 360–1280 px sin scroll horizontal · cero datos reales |
| Método de verificación | Cumple | Cumple | Cumple | Script con 20 peticiones · DevTools en 3 resoluciones + Lighthouse ≥ 90 · inspección de datos semilla y `.gitignore` |
| Responsable | Héctor Oviedo | Vicente Díaz | Héctor Oviedo | Medición en semana 3 y 4 |
| Evidencia planificada | `scripts/medir-rendimiento.js` (semana 3) | Capturas 360/1280 + Lighthouse (semanas 3–4) | Revisión de datos semilla (semana 4) | Pendiente de ejecución |

## 3. Mockups

| Criterio | Estado | Evidencia / observación |
|---|---|---|
| Búsqueda / listado con filtros | Parcial | `sem2-t1-busqueda.jpg` — tipo, fecha y bloque; tarjetas con estado “Disponible”. Repite “Sala 1” y los conteos no cuadran (HAL-07) |
| Reserva + QR (detalle, confirmación y QR) | Cumple | `sem2-t1-reserva-qr.jpg` — detalle, confirmación con QR e ID de reserva |
| Vista bibliotecario: validar inicio y devolución | Cumple | `sem2-t1-bibliotecario.jpg` — QR, datos de la reserva, “Confirmar entrega” y “Registrar devolución” |
| Login opcional / mínimo | No aplica | No se entregó; el login sigue siendo opcional según el plan |
| Mensajes de error como estados | Parcial | Presentes: límite diario (RF-06, lámina 2) y devolución tardía (RF-07, lámina 3). Faltan: recurso ocupado, QR inválido y QR duplicado → HAL-02 |
| Versión móvil 360 px en las 3 pantallas | Cumple | Las 3 láminas incluyen el marco móvil |
| Versión escritorio 1280 px en al menos 2 | Cumple | Las 3 láminas incluyen el marco de escritorio |
| Cada pantalla referencia su RF | Parcial | Láminas 1 y 2 con banda de título y chip de RF; lámina 3 sin ninguno → HAL-01 |
| Datos ficticios, sin datos reales | No cumple | Nombre real y correo con dominio institucional en las 3 láminas (HAL-06). Se reemplazan por “Estudiante 1” y estudiante1@example.com en la corrección de S2; el rediseño de S3 los mantiene ficticios |

## 4. UML

| Criterio | Estado | Evidencia / observación |
|---|---|---|
| Actores: Estudiante/Docente y Bibliotecario | Cumple | `docs/week-02/diagrams/casos-de-uso.mmd` — “Docente / Estudiante” y “Bibliotecario / Resolutor” |
| Casos: buscar, reservar, ver QR, validar inicio, devolver, sancionar | Cumple | CU1, CU2, CU3, CU4, CU5 y CU6; se agrega CU0 Iniciar Sesión (RF-08) |
| Secuencia del flujo principal | Cumple | `sem2-t2-diagrama-secuencia.png` — reserva completa desde la interfaz hasta la confirmación con QR |
| Rama de error: límite diario (RF-06) | Cumple | Diagrama de secuencia, bloque `alt` “Límite diario alcanzado (RF-06)” con rechazo y mensaje |
| Rama de error: usuario sancionado (RF-07) | Cumple | Diagrama de secuencia, bloque `alt` “Usuario sancionado (RF-07)” con rechazo y mensaje |
| Rama de error: recurso ocupado | Cumple | Diagrama de secuencia, bloque `alt` “Recurso ocupado” con rechazo y mensaje |
| Clases/entidades: Usuario, Recurso, Reserva, QR, Sanción | Cumple | `sem2-t2-diagrama-clases.png` — 5 clases con atributos, métodos y relaciones |
| Consistencia entre casos de uso, secuencia y clases | Cumple | Fuentes `.mmd` reconstruidas el 2026-11-05 desde los PNG entregados: coinciden en clases, participantes, mensajes y orden. La arquitectura que asume el diagrama es una decisión pendiente del grupo, no un defecto del artefacto (ver HAL-05) |
| Diagramas exportados y legibles | Cumple | 3 PNG integrados: `sem2-t2-casos-de-uso.png` (4520×2887), `sem2-t2-diagrama-clases.png` (1034×2046), `sem2-t2-diagrama-secuencia.png` (3946×3882) |

## 5. Casos de prueba y matriz

| Criterio | Estado | Evidencia / observación |
|---|---|---|
| 6 casos con todos los campos (12 al cierre) | Cumple | `qa/casos-prueba.md` — 6 casos con los 10 campos de la plantilla, verificados uno por uno |
| Plan de 12 casos (6 + 3 + 3) | Cumple | Declarado en `qa/casos-prueba.md` y `qa/matriz-trazabilidad.md`. CP-11 y CP-12 se adelantan a semana 3 |
| Al menos 1 caso negativo en semana 2 | Cumple | CP-04 — QR inválido o duplicado rechazado |
| Al menos 1 caso de límite en semana 2 | Cumple | CP-03 — tercera reserva del día; CP-06 — devolución 1 min después del bloque |
| Al cierre: ≥ 3 negativos y ≥ 2 de límites | Pendiente | El plan ya garantiza 5 positivos / 3 negativos / 4 límites; se verifica al ejecutar en semana 4 |
| Resultados `Pendiente` sin evidencia | Cumple | La matriz mantiene todo en `Pendiente` |
| Matriz con CP-01 a CP-12 y todos los RF/RNF | Cumple | 8 RF y 3 RNF con su caso asignado |
| Estado de implementación declarado | Cumple | “No implementado (semana 3/4)” en las 11 filas |

## 6. Informe

| Criterio | Estado | Evidencia / observación |
|---|---|---|
| Sección 1: problema y alcance | Pendiente | Borrador en Drive (T7) |
| Sección 2: requisitos y diseño | Pendiente | Borrador en Drive (T7) |
| Figuras referenciadas y legibles | Pendiente | Depende de T7 |
| Citas y referencias consistentes | Pendiente | Depende de T7 |
| Marcadores `[COMPLETAR]` visibles | Pendiente | Depende de T7 |
| Presupuesto ≈ 4,5 páginas | Pendiente | Depende de T7 |

## 7. Hallazgos y correcciones

| ID | Hallazgo | Artefacto | Severidad | Responsable | Corrección | Fecha | Re-revisión |
|---|---|---|---|---|---|---|---|
| HAL-01 | La lámina del bibliotecario no tiene banda de título ni chip de RF: no cumple “cada pantalla referencia su RF” | `sem2-t1-bibliotecario.jpg` | Media | Vicente Díaz | Agregar banda `[SEM2-T1] PANTALLA 3: VISTA BIBLIOTECARIO (RF-04, RF-05, RF-07)` y reexportar | [COMPLETAR] | Pendiente |
| HAL-02 | Faltan los estados de error de recurso ocupado, QR inválido y QR duplicado | `sem2-t1-reserva-qr.jpg`, `sem2-t1-bibliotecario.jpg` | Media | Vicente Díaz | Agregar los tres estados y reexportar, o declararlos pendientes para semana 3 | [COMPLETAR] | Pendiente |
| HAL-03 | Funciones fuera de alcance: “Descargar PDF” y “Descargar QR” (lámina 2), “Historial” y “Mis Reservas” (lámina 1) | `sem2-t1-busqueda.jpg`, `sem2-t1-reserva-qr.jpg` | Baja | Vicente Díaz | Eliminarlas o declararlas como mejora futura en el README de la tarea | [COMPLETAR] | Pendiente |
| HAL-04 | La sección de exportación de `T1-mockups.md` listaba 7 archivos `-mobile`/`-desktop`; lo entregado son 3 láminas con móvil y escritorio juntos | `local/week-02/T1-mockups.md` | Baja | Yordy Carmona | Actualizar la sección a los 3 nombres reales | 2026-11-04 | No aplica (documento local) |
| HAL-05 | Las fuentes `.mmd` del repo no correspondían a los PNG entregados | `clases.mmd`, `secuencia-reserva.mmd` | Media | Yordy Carmona | Fuentes reconstruidas el 2026-11-05 desde los PNG: 5 clases y 8 participantes con 27 mensajes; fuente y exportación coinciden | 2026-11-05 | Corregido |
| HAL-06 | Las 3 láminas incluyen el nombre real “Vicente Díaz” y un correo de apariencia institucional (ficticio, pero con dominio real) | `sem2-t1-busqueda.jpg`, `sem2-t1-reserva-qr.jpg`, `sem2-t1-bibliotecario.jpg` | Media | Vicente Díaz / Yordy Carmona | Reemplazar por “Estudiante 1” y `estudiante1@example.com` en las 3 láminas; el rediseño de S3 usa solo datos ficticios | 2026-11-06 | Corregido en S2; pendiente re-revisión 1:1 |
| HAL-07 | La pantalla 1 repite “Sala 1” y los conteos no cuadran: “Disponibles (3)”, “Mostrando 4 resultados” y 5 tarjetas | `sem2-t1-busqueda.jpg` | Media | Vicente Díaz | Corregir en el rediseño de S3 (SEM3-T1); se documenta en el informe | 2026-11-06 | Pendiente (S3) |

## 8. Resultado global

| Campo | Detalle |
|---|---|
| Ítems evaluados | 18 (9 de mockups + 9 de UML) |
| Cumple | 13 |
| No cumple / parcial | 4 |
| Pendiente | 0 |
| No aplica | 1 |
| Conclusión | Aprobado con cambios: mockups y los tres diagramas UML están integrados y son utilizables. HAL-06 se corrigió en S2 (datos ficticios); quedan abiertos HAL-01, HAL-02, HAL-03 y HAL-07 (mockups, Vicente Díaz) para el rediseño de S3. Las decisiones D-01 a D-05 quedaron tomadas: monolito modular, Django 5.2 LTS, SQLite, bloques de 60 min y QR por ingreso manual. |
| Revisor | Yordy Carmona |
| Fecha | 2026-11-04 (primera pasada) · 2026-11-05 (segunda pasada, T3 + T5 + T6) · 2026-11-06 (corrección HAL-06/HAL-07 y cierre de decisiones) |
