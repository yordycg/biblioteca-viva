# Revisión técnica del backend y scripts (S3-02)

| Campo | Detalle |
|---|---|
| Responsable | Héctor Oviedo Herrera |
| Período | Semana 3 |
| Fecha de ejecución | 2026-11-15 |
| Entorno | Python 3.12, `.venv`, Django 5.2, SQLite, datos ficticios |
| Alcance | `reservas/models.py`, `reservas/services.py`, `reservas/management/commands/seed.py`, `reservas/tests.py` y `scripts/` |

## 1. Archivos revisados

Se revisaron los modelos y las relaciones de datos, las reglas de negocio de
reservas y préstamos, la carga de datos de demostración y los scripts de flujo,
simulación de retraso, medición de rendimiento y panel.

- `reservas/models.py`: Usuario, Recurso, Libro, Reserva, QR y Sanción.
- `reservas/services.py`: búsqueda, reservas, préstamos, QR, entrega, devolución y sanción.
- `reservas/management/commands/seed.py`: datos ficticios y reservas de ejemplo.
- `reservas/tests.py`: suite automatizada de la aplicación.
- `scripts/demo_flujo.py`, `scripts/simular_retraso.py`, `scripts/medir_rendimiento.py`, `scripts/demo_dashboard.py` y `scripts/seed.py`.

## 2. Qué hace el backend

El backend de BibliotecaViva administra usuarios, recursos (salas y equipos) y
libros. Permite gestionar reservas por bloques y préstamos de libros, controlar
los estados de las reservas, generar y validar códigos QR, registrar devoluciones
y aplicar sanciones cuando corresponde. El comando `seed` carga datos ficticios
para facilitar la demostración y la revisión del sistema.

## 3. Preparación y resultados

El entorno se preparó con las dependencias de `requirements.txt`. En la primera
ejecución de `seed` se informó que no existía la tabla `reservas_usuario`: el
entorno no tenía las migraciones aplicadas. Se ejecutó `python manage.py migrate`
y, después, `seed` terminó correctamente. El `README.md` y el `justfile` ya
indican ese orden (`migrate` antes de `seed`); no es un defecto de código.

```bash
python manage.py migrate
python manage.py seed
```

Después de eso, `python manage.py check` no detectó problemas.

## 4. Veredicto por archivo

| Archivo | Veredicto | Observación |
|---|---|---|
| `reservas/models.py` | Sin observaciones | Los modelos y las relaciones cubren usuarios, recursos, libros, reservas, QR y sanciones; los estados son coherentes con el flujo. |
| `reservas/services.py` | Sin observaciones | La búsqueda, la reserva, el QR, la validación, la devolución, la sanción y los préstamos quedan cubiertos por la suite y por los scripts de demo. |
| `reservas/management/commands/seed.py` | Sin observaciones de código | Carga idempotente con `get_or_create`; programa las reservas de ejemplo con fechas relativas y admite `--reset` y `--fecha`. Requiere migraciones aplicadas. |
| `reservas/tests.py` | Sin observaciones | 90 pruebas ejecutadas y aprobadas; cubren los flujos y las reglas de negocio. |
| `scripts/` | Sin observaciones | `demo_flujo.py`, `simular_retraso.py` y `medir_rendimiento.py` ejecutados; `demo_dashboard.py` y `scripts/seed.py` revisados. |

No se modificó código en esta revisión y no se reportaron defectos de código. El
único incidente fue de entorno (migraciones), descrito en la sección 3.

## 5. Reglas verificadas

| Regla | Verificación | Evidencia |
|---|---|---|
| RF-06 — máximo 2 reservas activas por día | La tercera reserva del día se rechaza con mensaje y las dos anteriores se mantienen. | CP-03 aprobado; CP-19 pendiente; suite de 90 pruebas |
| RF-07 — devolución tardía | La devolución a las 11:01 deja la reserva Finalizada y aplica una sanción de 7 días; la reserva posterior se rechaza. | `scripts/simular_retraso.py`; CP-06 y CP-12 aprobados |
| RF-03 — QR único | Cada reserva genera un QR con su ID; el QR inválido y el duplicado se rechazan. | `scripts/demo_flujo.py`; CP-02 y CP-04 aprobados |
| RF-02 — préstamos de libros | Un libro no se presta si su rango se solapa con un préstamo activo; el usuario no supera 2 préstamos activos. | Suite de 90 pruebas; CP-18 y CP-19 pendientes de ejecución formal |
| RF-01 — catálogo con estado | La vista muestra todos los recursos con su estado y permite «Solo disponibles»; el seed carga salas, equipos y libros. | CP-01 y CP-11 aprobados; CP-20 pendiente |
| RNF-01 — rendimiento | Medición local del servicio + QR: 20 peticiones, promedio 19,9 ms y máximo 74,7 ms. Es una medición preliminar; la medición HTTP formal queda para S4. | `scripts/medir_rendimiento.py`; CP-08 sigue Pendiente |

Las reglas quedan cubiertas por la suite automatizada; los casos que aún no se
ejecutaron permanecen **Pendiente** en la matriz de trazabilidad.

## 6. Conclusión

Las cuatro ejecuciones solicitadas (`seed`, `demo_flujo.py`, `simular_retraso.py`
y `medir_rendimiento.py`), más `check` y la suite de 90 pruebas, finalizaron
correctamente después de aplicar las migraciones. No se encontraron defectos de
código en la revisión. La medición de rendimiento es preliminar y no reemplaza la
medición HTTP formal de S4.

## 7. Evidencias de terminal

### A. `python manage.py check`

```text
System check identified no issues (0 silenced).
```

### B. `python manage.py seed`

```text
Usuario: estudiante1@virginiogomez.cl (SOLICITANTE)
Usuario: estudiante2@virginiogomez.cl (SOLICITANTE)
Usuario: bibliotecario1@virginiogomez.cl (BIBLIOTECARIO)
Recurso: Sala 3
Recurso: Sala 1
Recurso: Proyector Epson
Recurso: Notebook Dell
Libro: Don Quijote de la Mancha
Libro: Martín Fierro
Libro: La Araucana
Libro: Veinte mil leguas de viaje submarino
Libro: La metamorfosis
Libro: Frankenstein
Reservas de ejemplo: 2026-11-15 · 17:00-18:00 y 18:00-19:00.
Reserva de ejemplo: RSV-0001 (Sala 1)
Reserva cancelada de ejemplo: RSV-0002 (Sala 3)
Seed listo.
Contraseña de todos los usuarios: demo1234
```

### C. `python scripts/demo_flujo.py`

```text
1. Búsqueda de recursos libres
   Disponibles: ['Sala 1', 'Sala 3']
2. Reserva + QR
   Reserva: RSV-0003 | estado: Reservada
3. Validación del QR
   Estado: En Uso
4. Devolución dentro del bloque
   Estado: Finalizada | sanción: None
Flujo completo OK.
```

### D. `python scripts/simular_retraso.py`

```text
Reserva: RSV-0004
Estado tras la entrega: En Uso
Estado tras la devolución: Finalizada
Sanción aplicada: 2026-11-12 11:01:00-03:00 → 2026-11-19 11:01:00-03:00
Usuario sancionado hasta: 2026-11-19 11:01:00-03:00
```

### E. `python scripts/medir_rendimiento.py`

```text
Peticiones: 20
Promedio: 19.9 ms
Máximo:   74.7 ms
Mínimo:   15.4 ms
Nota: medición local del servicio + QR; la medición HTTP formal se hace en S4.
```

### F. `python manage.py test reservas`

```text
Found 90 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
..........................................................................................
----------------------------------------------------------------------
Ran 90 tests in 111.420s

OK
Destroying test database for alias 'default'...
```

---

# Revisión de cierre y regresión (S4-T6)

| Campo | Detalle |
|---|---|
| Responsable | Héctor Oviedo Herrera (verifica) · ejecución del 2026-11-20 |
| Rama revisada | `week/sem4-5` en `v0.9-rc` |
| Alcance | Los archivos de S3 más `tests/` (suite separada por dominio) y los scripts de carga, auditoría y E2E |

## 1. Cambios revisados desde la revisión de S3

| Cambio | Archivo | Qué se verificó |
|---|---|---|
| DEF-03: bloques disponibles sin JavaScript | `reservas/forms.py` | `BusquedaForm` ofrece el catálogo completo cuando no hay fecha; `clean()` sigue rechazando bloques no disponibles, ya iniciados o fuera del horizonte de 7 días. La validación del servidor no se relajó: solo cambió el conjunto de opciones que ve el usuario |
| DEF-04: marcado válido | `templates/reservas/buscar.html`, `mis_reservas.html`, `styles.css` | Encabezado oculto en la sección de resultados; la lista de datos dejó de usar `dl` con envoltorio inválido. Las clases nuevas (`data-list__term`, `data-list__value`) reemplazan a `dt`/`dd` sin cambiar el aspecto |
| DEF-05: antelación visible | `templates/reservas/buscar.html` | El texto de ayuda usa `services.MIN_ANTELACION_MIN`; si la constante cambia, el mensaje cambia con ella |
| Suite separada por dominio | `tests/test_reglas.py`, `test_reservas.py`, `test_inventario.py`, `test_libros.py`, `test_interfaz.py` | 91 pruebas; ninguna prueba modificada para que pasara, salvo las dos de regresión agregadas con DEF-03 |

## 2. Revisión de los scripts nuevos

| Script | Riesgo | Observación |
|---|---|---|
| `scripts/auditar_lighthouse.py` | Bajo | Solo lectura; inicia sesión con usuarios ficticios y escribe en `docs/evidence/` |
| `scripts/validar_w3c.py` | Bajo | Solo lectura; requiere `vnu.jar` y un JRE, declarados en el README |
| `scripts/prueba_e2e.py` | Medio | Crea una reserva real en la base de pruebas; exige `DEMO_MODE=1` para no depender de la hora. Se ejecuta sobre el seed reiniciado |
| `scripts/carga/` (JMeter) | Medio | Genera reservas y carga contra el servidor; se ejecuta sobre una base sembrada y se reinicia después |
| `requirements-dev.txt` | Bajo | `gunicorn` y `selenium` son dependencias de prueba: la aplicación no las importa en ejecución |

## 3. Regresión sobre la rama final

```text
Found 91 test(s).
System check identified no issues (0 silenced).
Ran 91 tests
OK
```

Complementada con la regresión funcional del 2026-11-20:

- CP-26 re-ejecutado sin JavaScript tras DEF-03 → aprobado.
- Flujo completo con Selenium → 8 de 8 pasos.
- Validador del W3C → 0 errores en cinco pantallas.
- Lighthouse → 100 de accesibilidad en seis auditorías.

## 4. Conclusión de la revisión

Sin hallazgos bloqueantes. Las dos correcciones de producto (DEF-03 y DEF-04) no
relajan ninguna regla del servidor: una amplía las opciones visibles y la otra
corrige el marcado. La separación de la suite por dominio no cambió la cobertura
(91 pruebas antes y después de la corrección de DEF-03, sumando las dos de
regresión).

Pendiente declarado: la sesión de validación con usuario final (S4-T8) no se
ejecutó; la usabilidad se respalda con Lighthouse, la validación del W3C y el
flujo automatizado.
