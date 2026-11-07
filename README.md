# BibliotecaViva — Sistema de Gestión y Reservas

Aplicación web responsiva para buscar, reservar y validar salas y equipos de la biblioteca del Instituto Profesional Virginio Gómez. Es la Evaluación 3 de Ingeniería de Software.

## Estado actual

- Semana 1: ficha, requisitos y plan de calidad.
- Semana 2: diseño y QA base (mockups, UML, checklist, matriz y 6 casos).
- Semana 3: MVP Django de F1–F3.

## Stack

- Python 3.12 + Django 5.2 LTS + SQLite.
- Templates de Django + CSS propio, mobile-first.
- QR generado en el servidor con `qrcode`.
- Validación del QR por ingreso manual del código.
- Monolito modular: `config/` + `reservas/`.

## Estructura

```text
config/                 # settings y urls
reservas/
  models.py             # Usuario, Recurso, Reserva, QR, Sancion
  services.py           # RF-06 y RF-07
  views.py              # login, búsqueda, reserva, QR, bibliotecario
  forms.py
  urls.py
  templates/reservas/
  static/reservas/
  management/commands/seed.py
scripts/
  demo_flujo.py
  simular_retraso.py
  medir_rendimiento.py
requirements.txt
.env.example
```

## Requisitos

- Python 3.12 o superior.
- pip.
- No requiere Node, Docker ni servicios externos.

## Instalación y ejecución

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed
python manage.py runserver 0.0.0.0:8000
```

Abrir en el navegador: `http://localhost:8000`.

Para acceder desde un teléfono en la misma red, usar `http://IP-DEL-PC:8000` y agregar esa IP en `DJANGO_ALLOWED_HOSTS` y `DJANGO_CSRF_TRUSTED_ORIGINS` si hace falta.

## Credenciales ficticias

| Rol | Usuario | Contraseña |
|---|---|---|
| Estudiante | `estudiante1@example.com` | `demo1234` |
| Estudiante | `estudiante2@example.com` | `demo1234` |
| Bibliotecario | `bibliotecario1@example.com` | `demo1234` |

## Flujo principal

1. El estudiante inicia sesión.
2. Busca por tipo, fecha y bloque.
3. Selecciona un recurso disponible y confirma la reserva.
4. Se muestra el QR con el ID `RSV-NNNN`.
5. El bibliotecario ingresa el código manualmente y confirma la entrega.
6. El bibliotecario registra la devolución; si es tardía, se aplica una sanción de 7 días.

## Scripts de demo

```bash
.venv/bin/python scripts/seed.py
.venv/bin/python scripts/demo_flujo.py
.venv/bin/python scripts/simular_retraso.py
.venv/bin/python scripts/medir_rendimiento.py
```

- `demo_flujo.py` recorre búsqueda → reserva → QR → entrega → devolución.
- `simular_retraso.py` fuerza una devolución a las 11:01 y muestra la sanción.
- `medir_rendimiento.py` mide 20 reservas + QR a nivel de servicio (medición inicial de RNF-01).

## Modo demostración

Para probar RF-07 sin esperar la hora real:

```bash
DEMO_MODE=1 DEMO_NOW=2026-11-12T11:01:00 python manage.py runserver 0.0.0.0:8000
```

`DEMO_MODE` desactiva la validación estricta de fecha/hora y `DEMO_NOW` fija la hora de la aplicación. No usar en producción.

## Datos y seguridad

- Todos los datos son ficticios.
- No se incluyen credenciales, tokens ni datos personales reales.
- Las contraseñas se almacenan con el hash de Django.
- `db.sqlite3` y `.env` están fuera de Git.
- El QR se valida por ingreso manual; la cámara queda como mejora futura.

## Documentación

- [`docs/week-01/01-ficha-proyecto.md`](docs/week-01/01-ficha-proyecto.md)
- [`docs/week-01/02-requisitos.md`](docs/week-01/02-requisitos.md)
- [`docs/week-01/03-plan-calidad.md`](docs/week-01/03-plan-calidad.md)
- [`docs/week-02/README.md`](docs/week-02/README.md)
- [`docs/week-02/qa/casos-prueba.md`](docs/week-02/qa/casos-prueba.md)
- [`docs/week-02/qa/matriz-trazabilidad.md`](docs/week-02/qa/matriz-trazabilidad.md)

## Uso de IA

El docente indicó que el equipo podía usar IA para construir el proyecto. El código fue generado con asistencia de IA bajo especificación del equipo y revisado por sus integrantes. La declaración completa se incluye en el informe SEM-03. Los prompts y notas de trabajo viven en `local/` y no se versionan.
