# BibliotecaViva — Sistema de Gestión y Reservas

Aplicación web responsiva para buscar, reservar y validar salas y equipos de la biblioteca del Instituto Profesional Virginio Gómez. Es la Evaluación 3 de Ingeniería de Software.

## Estado actual

- Semana 1: ficha, requisitos y plan de calidad.
- Semana 2: diseño y QA base (mockups, UML, checklist, matriz y 6 casos).
- Semana 3: MVP Django de F1–F3 con interfaz institucional (port del rediseño SEM3-T1 a CSS propio).

## Stack

- Python 3.12 + Django 5.2 LTS + SQLite.
- Templates de Django + CSS propio mobile-first (sin Tailwind, sin CDN, sin fuentes ni imágenes remotas).
- Iconografía con sprite SVG inline; JavaScript mínimo y progresivo.
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
  templates/reservas/     # base, login, búsqueda, reserva, QR, mis reservas, panel
  static/reservas/        # styles.css, app.js
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

## Inicio rápido

### Primera vez

```bash
git clone https://github.com/yordycg/biblioteca-viva.git
cd biblioteca-viva
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed
python manage.py runserver 0.0.0.0:8000
```

Abrir `http://localhost:8000`.

### Si ya tienes el entorno

```bash
cd biblioteca-viva
source .venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

Si la base está vacía:

```bash
python manage.py migrate
python manage.py seed
```

Para reiniciar los datos: `python manage.py seed --reset`.

Para acceder desde un teléfono en la misma red:

```bash
DJANGO_ALLOWED_HOSTS="*" DJANGO_CSRF_TRUSTED_ORIGINS="http://IP-DEL-PC:8000" python manage.py runserver 0.0.0.0:8000
```

## Credenciales ficticias

| Rol | Usuario | Contraseña |
|---|---|---|
| Estudiante | `estudiante1@example.com` | `demo1234` |
| Estudiante | `estudiante2@example.com` | `demo1234` |
| Bibliotecario | `bibliotecario1@example.com` | `demo1234` |

## Pantallas para revisar

| Pantalla | Ruta | Qué revisar |
|---|---|---|
| Login | `/login/` | Formulario, mensajes de error |
| Búsqueda | `/buscar/` | Filtros, tarjetas, estado vacío |
| Reserva | clic en “Reservar bloque” | Detalle y confirmación |
| QR | `/reserva/<id>/qr/` | QR legible e ID |
| Mis reservas | `/mis-reservas/` | Reservas activas, historial y reapertura del QR |
| Bibliotecario | `/bibliotecario/` | Código manual, tabla del día, entrega y devolución |
| Admin | `/admin/` | Solo para desarrollo; no es parte del flujo |

## Revisión por rol

| Rol | Dónde revisar | Qué entregar |
|---|---|---|
| Vicente (UI) | `/login/`, `/buscar/`, reserva, QR y `/bibliotecario/`; DevTools en 360 y 1280 | 3 capturas + 3 observaciones |
| Héctor (backend) | `reservas/models.py`, `reservas/services.py`, `reservas/management/commands/seed.py`, `scripts/`; ejecutar `seed`, `demo_flujo` y `simular_retraso` | Nota de 1 página + salida de scripts |
| Héctor (medición) | `python scripts/medir_rendimiento.py` | Salida con promedio y máximo |
| Gerald (QA) | App + `docs/week-03/qa/casos-prueba.md` | 6 evidencias + matriz actualizada |
| Lucas (docs) | `README.md` + informe SEM-03 | Documentos finales en Drive |
| Yordy (integración) | `manage.py check`, `manage.py test` y flujo completo | PR actualizado, demo y tag |

## Problemas comunes

- **Puerto ocupado:** `python manage.py runserver 8001`.
- **`DisallowedHost`:** agrega la IP a `DJANGO_ALLOWED_HOSTS`.
- **CSRF en el teléfono:** agrega el origen a `DJANGO_CSRF_TRUSTED_ORIGINS`.
- **No hay usuarios:** `python manage.py migrate && python manage.py seed`.
- **Datos sucios:** `python manage.py seed --reset`.
- **Login falla:** usa `estudiante1@example.com` / `demo1234`.

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
# Entrega y devolución dentro del bloque
DEMO_MODE=1 DEMO_NOW=2026-11-10T10:45:00 python manage.py runserver 0.0.0.0:8000

# Devolución tardía (sanción)
DEMO_MODE=1 DEMO_NOW=2026-11-12T11:01:00 python manage.py runserver 0.0.0.0:8000
```

`DEMO_MODE` desactiva la validación estricta de fecha/hora y `DEMO_NOW` fija la hora de la aplicación. No usar en producción.

Con `DEMO_MODE=1`, la búsqueda y el panel del bibliotecario abren en la fecha de
`DEMO_NOW`, de modo que la reserva de ejemplo del seed queda a la vista.

## Interfaz

El rediseño de la semana 3 se implementó con CSS propio: no hay Tailwind, CDN,
Google Fonts ni imágenes remotas, así que la aplicación se ve igual sin conexión.

- Tokens y componentes: [`docs/week-03/design/design-system.md`](docs/week-03/design/design-system.md).
- Estilos: `reservas/static/reservas/styles.css`.
- Iconos: sprite SVG inline en `reservas/templates/reservas/_icons.html`.
- Interacción opcional: `reservas/static/reservas/app.js` (mostrar contraseña,
  cargar credenciales de demostración, confirmar devolución). Sin JavaScript, los
  formularios siguen funcionando.

Para revisar la responsividad, abre las pantallas a 360×800 y 1280×800 y compara
con `docs/week-03/evidence/rnf-02/`.

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
- [`docs/week-03/README.md`](docs/week-03/README.md)
- [`docs/week-03/design/design-system.md`](docs/week-03/design/design-system.md)
- [`docs/week-03/qa/casos-prueba.md`](docs/week-03/qa/casos-prueba.md)
- [`docs/week-03/qa/matriz-trazabilidad.md`](docs/week-03/qa/matriz-trazabilidad.md)

## Uso de IA

El docente indicó que el equipo podía usar IA para construir el proyecto. El código fue generado con asistencia de IA bajo especificación del equipo y revisado por sus integrantes. La declaración completa se incluye en el informe SEM-03. El material de trabajo interno no se versiona.
