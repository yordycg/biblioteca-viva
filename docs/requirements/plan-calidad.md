# Plan de Calidad y Metodología

> Responsable: Yordy Carmona (Líder, Git Master & QA Reviewer). Revisión: 2026-11-20.
> Este plan se aplica a todo el proyecto; cada métrica tiene umbral, herramienta,
> responsable y evidencia. Lo que no tiene evidencia no se declara cumplido.

## 1. Metodología y roles

- **Metodología:** Scrum con sprints semanales y revisión formativa del docente.
- **Roles:** Yordy Carmona (líder, Git Master y QA reviewer) · Vicente Díaz
  (frontend y mockups) · Héctor Oviedo (backend y scripts) · Gerald Sobarzo (QA,
  casos y trazabilidad) · Lucas Jara (documentación e informe).

| Rol | Responsabilidad de calidad |
|---|---|
| Líder / QA reviewer | Plan de calidad, revisión de PR, tags, medición de RNF y evidencias |
| Frontend | Mockups, responsividad, accesibilidad y mensajes de error legibles |
| Backend | Lógica de RF, datos semilla, scripts y regresiones |
| Analista QA | Casos de prueba, matriz de trazabilidad, bitácora de defectos |
| Documentador | Consistencia del informe, del manual y de las cifras con la evidencia |

## 2. Mecanismos de calidad

- **Ramas y PR:** una rama semanal (`week/semN`) con PR obligatorio; `main` solo
  recibe merges aprobados. Un PR de integración y uno de correcciones por semana.
- **Revisión cruzada:** cada artefacto lo revisa alguien distinto de quien lo
  produjo; la observación queda en el PR o en la bitácora.
- **DoD:** criterio de aceptación cumplido, evidencia enlazada, matriz
  actualizada, sin datos reales y documentación al día.
- **Trazabilidad:** todo RF/RNF tiene al menos un caso `CP-XX` con evidencia.
- **Congelamiento:** terminada la semana 4 no se agregan funcionalidades; solo se
  corrigen defectos con `DEF-XX` y su re-prueba.

## 3. Métricas, umbrales y evidencia

| Req. | Métrica | Umbral | Herramienta | Evidencia | Resultado |
|---|---|---|---|---|---|
| RNF-01 | Confirmar reserva y emitir QR | promedio ≤ 1,5 s (20 peticiones) | Script HTTP propio | `evidence/CP-08.txt` | 27 ms |
| RNF-01 | Carga concurrente (1/10/50 usuarios) | sin errores; punto de saturación declarado | JMeter 5.6.3 | `evidence/rnf-01-estres/` | 0 % error; techo ≈ 27 req/s; p95 896 ms a 10 usuarios |
| RNF-02 | Accesibilidad | ≥ 90 | Lighthouse 12.8.2 | `evidence/rnf-02/lighthouse/` | 100 |
| RNF-02 | Buenas prácticas | ≥ 90 | Lighthouse 12.8.2 | `evidence/rnf-02/lighthouse/` | 96 |
| RNF-02 | Adaptación 360 / 768 / 1280 px | sin scroll horizontal | DevTools + capturas | `evidence/rnf-02/` | Cumple |
| RNF-02 | Validez del HTML | 0 errores | Validador Nu del W3C | `evidence/w3c/` | 0 errores y 0 avisos |
| RNF-03 | Datos ficticios y hash | 0 credenciales reales; PBKDF2 | Revisión + `.gitignore` | `evidence/CP-10.png` | Cumple |
| Funcional | Casos ejecutados | ≥ 12 (≥ 3 negativos, ≥ 2 límite) | Casos manuales + Selenium | `qa/casos-prueba.md` | 27 casos: 14 positivos, 6 negativos y 7 de límite |
| Funcional | Cobertura automatizada | suite en verde | `manage.py test` | 91 pruebas | Verde |
| Funcional | Flujo completo en navegador | 8 de 8 pasos | Selenium 4 | `evidence/e2e/` | 8 de 8 |

## 4. Gestión de defectos

1. Se registra con `DEF-XX` solo si se reproduce en la aplicación.
2. Severidad por impacto: crítica (bloquea o pierde datos), alta (regla de
   negocio mal aplicada), media (mensaje o estado confuso), baja (texto,
   marcado o detalle visual).
3. Cada corrección enlaza su commit y **obliga** a una re-prueba con los mismos
   datos; la columna «Re-prueba» no se completa sin esa ejecución.
4. Un caso con defecto abierto queda «Fallido» hasta su re-prueba.

Resultado del proyecto: 6 defectos registrados (3 de documentación y 3 de
producto: DEF-03, DEF-04 y DEF-05), todos cerrados con re-prueba.

## 5. Observaciones docentes y su seguimiento

| ID | Observación | Acción | Caso | Estado |
|---|---|---|---|---|
| OBS-01 | El login no mostraba credenciales de demostración | Credenciales ficticias documentadas en README y manual | CP-07 | Cerrada |
| OBS-02 | Se aceptaban fechas anteriores al día actual | Validación en formulario y servidor | CP-15 | Cerrada |
| OBS-03 | El panel no mostraba el estado del inventario | Inventario por recurso y bloque con contadores | CP-16 | Cerrada |
| OBS-04 | Faltaba explicitar la ventana de reserva y el catálogo de libros | Antelación de 15 min, horizonte de 7 días, catálogo de libros con ficha y préstamo | CP-17, CP-18, CP-19 | Cerrada |

Cada observación se verificó con su caso y su captura antes de cerrarla; no hay
observaciones cerradas sin evidencia.

## 6. Criterio de salida

El proyecto se declara terminado cuando: el flujo principal se ejecuta de punta a
punta en un clon limpio, los 27 casos tienen evidencia, no quedan defectos
abiertos, los umbrales de la tabla §3 se cumplen y el informe cita las mismas
cifras que la evidencia.
