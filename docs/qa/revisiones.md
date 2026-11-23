# Registro de revisiones internas

> Responsable: Yordy Carmona (Líder, Git Master & QA Reviewer). Revisión: 2026-11-23.
> Este registro anota quién revisó cada artefacto, qué observación surgió y qué se
> corrigió. No se registran aprobaciones formales que no hayan existido: la
> revisión fue documental, apoyada en el checklist, el historial de commits y el PR.

## 1. Revisión de artefactos — semana 2

| Artefacto | Autor | Revisor | Observaciones | Decisión | Corrección | Evidencia |
|---|---|---|---|---|---|---|
| Mockups F1–F3 | Vicente Díaz | Yordy Carmona | 5 hallazgos del checklist de diseño (HAL-01, -02, -03, -06, -07) | Con cambios | HAL-06 corregido; rediseño v2 en la semana 3 | [`design/mockups/`](../design/mockups/) |
| Casos de uso | Lucas Jara | Yordy Carmona | Sin observación | Sin cambios | — | [`design/diagrams/casos-de-uso.mmd`](../design/diagrams/casos-de-uso.mmd) |
| Diagrama de secuencia y clases | Héctor Oviedo | Yordy Carmona | OBS-LOCAL-02: las fuentes `.mmd` no generaban los PNG entregados | Con cambios | Fuentes reconstruidas el 2026-11-05 | [`design/diagrams/`](../design/diagrams/) |
| Checklist de diseño | Yordy Carmona | Autoevaluación en dos pasadas | HAL-06, HAL-07 y D-01 a D-05 | Sin cambios | El propio checklist recoge la segunda pasada | [`design/checklist-diseno.md`](../design/checklist-diseno.md) |
| Matriz de trazabilidad | Gerald Sobarzo | Yordy Carmona | OBS-LOCAL-01: CP-08 clasificado como positivo siendo de límite | Con cambios | CP-08 reclasificado a Límite | [`qa/matriz-trazabilidad.md`](matriz-trazabilidad.md) |
| Casos de prueba (6 iniciales) | Gerald Sobarzo | Yordy Carmona | OBS-LOCAL-01: misma clasificación de CP-08 | Con cambios | Distribución ajustada a 5 positivos, 3 negativos y 4 de límite | [`qa/casos-prueba.md`](casos-prueba.md) |
| Informe, secciones 1–2 | Lucas Jara | Yordy Carmona | Borrador sin citas consistentes | Con cambios | Versión revisada del informe semanal | Informe entregado en Canvas |

## 2. Revisión de las semanas 3 a 5

La revisión de estas semanas se apoyó en tres piezas, todas en el repositorio:

- **Revisión técnica del backend y los scripts**: [`qa/revision-backend.md`](revision-backend.md).
- **Revisión de la ejecución de casos**: cada caso de [`qa/casos-prueba.md`](casos-prueba.md) tiene su captura y su fecha de ejecución.
- **Correcciones y re-pruebas**: [`qa/defectos.md`](defectos.md), donde cada `DEF-XX` enlaza su commit y su re-prueba.

Las herramientas del cierre (Lighthouse, validador del W3C, JMeter y Selenium)
encontraron DEF-04 y DEF-05, y su re-prueba quedó registrada en la bitácora.

## 3. Observaciones internas

| ID | Observación | Corrección aplicada | Estado |
|---|---|---|---|
| OBS-LOCAL-01 | CP-08 estaba clasificado como positivo y verifica el borde del umbral de RNF-01 | Reclasificado como caso de límite en la matriz y en el documento de casos | Cerrada |
| OBS-LOCAL-02 | Las fuentes `.mmd` no generaban los PNG entregados | Fuentes reconstruidas desde los PNG (5 clases, 8 participantes, 27 mensajes) | Cerrada 2026-11-05 |

## 4. Observaciones del docente

Las cuatro observaciones de la revisión docente, con su acción, su caso de prueba
y su estado, están en [`requirements/plan-calidad.md`](../requirements/plan-calidad.md) §5.
