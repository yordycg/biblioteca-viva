# Manual de ejecución — BibliotecaViva

**Evaluación 3 — Ingeniería de Software**

Instituto Profesional Virginio Gómez

Versión 1.0 — 2026-11-15

## 1. Presentación

BibliotecaViva es una aplicación web responsiva para buscar, reservar y validar
salas, equipos y libros de la biblioteca. Este manual explica cómo instalar,
iniciar y recorrer el flujo principal con datos ficticios.

El alcance cubre las tres funcionalidades prioritarias:

- **F1 — Búsqueda (RF-01):** catálogo por tipo, fecha y bloque, con el estado de
  cada recurso y el filtro «Solo disponibles».
- **F2 — Reserva con QR (RF-02, RF-03, RF-06):** reserva de salas, equipos y
  libros, comprobante con QR y tope de 2 reservas activas por día.
- **F3 — Validación y devolución (RF-04, RF-05, RF-07):** entrega y devolución
  validadas por el bibliotecario, con sanción de 7 días por atraso.

La autenticación básica (RF-08) usa usuarios ficticios con roles de solicitante y
bibliotecario. El sistema no usa servicios externos, credenciales reales ni datos
personales.

## 2. Requisitos de ejecución

- Python 3.12 o superior.
- `pip` y un entorno virtual.
- SQLite (incluido con Python).
- No requiere Node, Docker, Redis ni conexión a internet.
- Opcional: `just` para ejecutar los atajos del `justfile`.

## 3. Instalación y primera ejecución

### 3.1 Primera vez

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

El orden importa: `migrate` crea las tablas y `seed` carga los datos ficticios.
Si se ejecuta `seed` antes de `migrate`, el comando falla porque la tabla
`reservas_usuario` todavía no existe.

### 3.2 Atajos con `just`

```bash
just setup       # venv, dependencias, migraciones y seed
just run         # servidor en 0.0.0.0:8000
just run-lan IP  # servidor para revisar desde el teléfono
```

### 3.3 Reiniciar los datos

```bash
python manage.py seed --reset
```

Para fijar la fecha de las reservas de ejemplo:

```bash
python manage.py seed --reset --fecha 2026-11-12
```

El seed programa sus reservas de ejemplo en el primer bloque reservable de hoy o,
si ya no quedan, en el primero de mañana.

### 3.4 Acceso desde otro dispositivo

```bash
DJANGO_ALLOWED_HOSTS="*" \
DJANGO_CSRF_TRUSTED_ORIGINS="http://IP-DEL-PC:8000" \
python manage.py runserver 0.0.0.0:8000
```

## 4. Datos ficticios y credenciales

| Rol | Usuario | Contraseña |
|---|---|---|
| Solicitante | `estudiante1@example.com` | `demo1234` |
| Solicitante | `estudiante2@example.com` | `demo1234` |
| Bibliotecario | `bibliotecario1@example.com` | `demo1234` |

Recursos de ejemplo: Sala 1 y Sala 3 (Piso 1), Proyector Epson (eq-014) y Notebook
Dell (eq-002). Libros: Don Quijote de la Mancha, Martín Fierro, La Araucana,
Veinte mil leguas de viaje submarino, La Metamorfosis y Frankenstein.

Todos los datos son ficticios. Las contraseñas se almacenan con el hash de Django
y el archivo `db.sqlite3` queda fuera de Git.

## 5. Flujo principal

### 5.1 Iniciar sesión

Abrir `/login/` e ingresar con `estudiante1@example.com` / `demo1234`. El
solicitante llega a la vista de búsqueda; el bibliotecario llega al panel de
gestión. Si las credenciales son incorrectas, se muestra «Correo o contraseña
incorrectos».

![Pantalla de login](docs/week-03/evidence/rnf-02/rnf-02-login-1280.png)

### 5.2 Buscar salas y equipos

En **Buscar → Salas y equipos**, elegir tipo, fecha y bloque, y presionar
**Filtrar**. La vista muestra todos los recursos del bloque con su estado:
«Disponible», «Reservado», «En uso» o «No disponible». Los recursos ocupados no
ofrecen botón de reserva.

La casilla **Solo disponibles** oculta los recursos ocupados. Los filtros inician
vacíos: la vista no muestra resultados hasta elegir fecha y bloque. El horizonte
de reserva es de 7 días y, para el día actual, solo se ofrecen bloques que
comienzan al menos 15 minutos después de la hora actual.

![Búsqueda de recursos](docs/week-03/evidence/rnf-02/rnf-02-buscar-1280.png)

En la pestaña **Libros** se puede filtrar por título, autor o género y abrir la
ficha del libro. La ficha muestra carátula, autor, editorial, año, ISBN, páginas,
ubicación y sinopsis.

### 5.3 Reservar y obtener el QR

En una tarjeta disponible, presionar **Reservar bloque …**. En el detalle,
verificar recurso, fecha y bloque, y presionar **Confirmar reserva**.

La aplicación registra la reserva, bloquea el recurso para ese bloque y muestra el
comprobante con un código QR y el ID `RSV-NNNN`. El QR se puede descargar o
volver a abrir desde **Mis reservas**.

![Comprobante con QR](docs/week-03/evidence/rnf-02/rnf-02-qr-1280.png)

### 5.4 Validar la entrega

El bibliotecario entra a **Panel → Validación**, escribe el código del QR o el ID
de la reserva y presiona **Buscar reserva**. La tarjeta muestra el solicitante, el
recurso, el bloque y el estado. Al presionar **Confirmar entrega**, la reserva
pasa a **En Uso**.

Un código inexistente se rechaza con «No existe una reserva con el código …». Un
código ya utilizado se rechaza con «QR ya utilizado o la reserva no está
vigente.».

### 5.5 Registrar la devolución

En **Panel → Validación**, buscar la reserva **En Uso** y presionar **Registrar
devolución**. Si la devolución ocurre dentro del bloque, la reserva pasa a
**Finalizada** y el recurso queda disponible, sin sanción.

Si la devolución ocurre después del término del bloque, la reserva también queda
**Finalizada**, pero se aplica una sanción de 7 días al solicitante. El aviso
«Devolución tardía: se aplicó una sanción de 7 días a …» y la sección
**Sanciones activas** muestran la fecha de término.

Mientras la sanción está vigente, el solicitante no puede reservar: la búsqueda
muestra el aviso «Sanción vigente» y la confirmación se rechaza con «No puedes
reservar: tienes una sanción vigente hasta DD-MM-YYYY HH:MM.».

### 5.6 Tope diario de reservas

Cada solicitante puede mantener **2 reservas activas por día**. Al intentar una
tercera, la aplicación rechaza la operación con «Límite alcanzado: ya tienes 2
reservas activas para ese día.» y conserva intactas las dos anteriores.

### 5.7 Préstamo de libros

En **Buscar → Libros**, abrir la ficha de un libro y elegir la fecha de retiro y
la duración (3, 7 o 14 días). Al confirmar, se genera un comprobante con QR y el
préstamo aparece en **Mis reservas** con su fecha de devolución.

Un libro no se puede prestar si su rango se solapa con un préstamo activo. El
usuario no puede superar 2 préstamos activos.

### 5.8 Mis reservas y cancelación

En **Mis reservas** se separan las reservas **Activas** del **Historial**. El
botón **Ver QR** reabre el comprobante de una reserva activa.

Una reserva pendiente de entrega se puede cancelar con un motivo. La reserva pasa
a **Cancelada**, se libera el bloque y el cupo diario, y el QR anterior deja de ser
válido. Una reserva **En Uso** no se cancela: se registra como devolución.

![Mis reservas](docs/week-03/evidence/rnf-02/rnf-02-mis-reservas-1280.png)

### 5.9 Panel del bibliotecario

El panel agrupa la operación en cuatro pestañas:

- **Operación:** KPIs del día, próximas entregas, devoluciones de libros,
  sanciones activas y ocupación por bloque.
- **Inventario:** estado de cada recurso por bloque, con filtros por nombre, tipo
  y estado.
- **Reservas del día:** tabla filtrable por estado y por código.
- **Validación:** ingreso manual del código para entregar o devolver.

La barra superior muestra el nombre del usuario, no el rol.

![Panel del bibliotecario](docs/week-03/evidence/rnf-02/rnf-02-bibliotecario-1280.png)

### 5.10 Interfaz responsiva

La interfaz está pensada para móvil y escritorio. Las capturas de referencia
están a 360×900 y 1280×900 en `docs/week-03/evidence/rnf-02/`; la interfaz no
presenta desplazamiento horizontal en esas resoluciones.

## 6. Errores y límites

| Situación | Comportamiento esperado | Requisito |
|---|---|---|
| Tercera reserva activa del día | Se rechaza con el mensaje del tope; las dos anteriores se mantienen. | RF-06 |
| Devolución después del bloque | La reserva queda Finalizada y se aplica una sanción de 7 días. | RF-07 |
| Devolución exactamente a la hora límite | No se aplica sanción; el límite es el fin del bloque inclusive. | RF-07 |
| QR inexistente | Se rechaza con «No existe una reserva con el código …». | RF-04 |
| QR ya utilizado | Se rechaza con «QR ya utilizado o la reserva no está vigente.». | RF-04 |
| Fecha anterior a hoy | La búsqueda y la confirmación por URL forzada se rechazan. | RF-01, RF-02 |
| Bloque ya iniciado o sin 15 minutos de antelación | No se ofrece en la búsqueda y el servidor lo rechaza. | RF-01, RF-02 |
| Reserva ajena | No aparece en la lista y el QR responde 404. | RF-03, RF-08 |
| Cancelación sin motivo | Se rechaza y la reserva no cambia de estado. | RF-02 |
| Libro con préstamo activo solapado | Se rechaza el nuevo préstamo. | RF-02, RF-06 |



## 7. Scripts de verificación

Con el entorno virtual activado:

```bash
python manage.py check
python manage.py test reservas
python scripts/demo_flujo.py
python scripts/simular_retraso.py
python scripts/medir_rendimiento.py
python scripts/demo_dashboard.py
```

- `check`: verifica la configuración de Django.
- `test reservas`: ejecuta la suite automatizada (90 pruebas al cierre de S3).
- `demo_flujo.py`: búsqueda → reserva → QR → entrega → devolución.
- `simular_retraso.py`: fuerza una devolución a las 11:01 y muestra la sanción.
- `medir_rendimiento.py`: mide 20 reservas + QR a nivel de servicio. Es una
  medición preliminar de RNF-01; la medición HTTP formal se realiza en S4.
- `demo_dashboard.py`: carga reservas, préstamos y una sanción ficticia para ver el
  panel del bibliotecario.

## 8. Problemas comunes

- **Puerto ocupado:** `python manage.py runserver 8001`.
- **`DisallowedHost`:** agregar la IP a `DJANGO_ALLOWED_HOSTS`.
- **CSRF en el teléfono:** agregar el origen a `DJANGO_CSRF_TRUSTED_ORIGINS`.
- **No hay usuarios:** ejecutar `python manage.py migrate` y luego
  `python manage.py seed`.
- **Datos sucios:** `python manage.py seed --reset`.
- **Login falla:** usar `estudiante1@example.com` / `demo1234`.
- **Sanción o reserva fuera de fecha:** revisar `DEMO_MODE` y `DEMO_NOW`, y
  volver a sembrar con `--fecha` si es necesario.

## 9. Evidencias y trazabilidad

- Casos de prueba: `docs/week-03/qa/casos-prueba.md`.
- Matriz de trazabilidad: `docs/week-03/qa/matriz-trazabilidad.md`.
- Bitácora de defectos: `docs/week-03/qa/defectos.md`.
- Evidencias de ejecución: `docs/week-03/evidence/`.
- Revisión de backend y scripts: `docs/week-03/qa/revision-backend.md`.

Al cierre de la semana 3 hay **11 casos aprobados** (CP-01 a CP-07 y CP-11 a
CP-14) y **90 pruebas automatizadas** aprobadas. CP-08 (rendimiento HTTP), CP-09
(Lighthouse) y CP-10 (auditoría de seguridad) quedan para S4, junto con los casos
CP-15 a CP-26 que aún no se ejecutan. La bitácora registra DEF-01 como una
corrección del caso CP-01 (criterio desactualizado respecto del RF-01 vigente), no
como un defecto de la aplicación.

## 10. Limitaciones y pendientes

- La validación del QR es por ingreso manual del código; la lectura con cámara
  queda como mejora futura.
- La medición de RNF-01 es preliminar (servicio + QR); falta la medición HTTP
  formal y su registro.
- La auditoría de accesibilidad con Lighthouse y la revisión formal de RNF-03
  quedan para S4.
- No se incorporan funcionalidades nuevas en la semana 5; el alcance está
  congelado en F1–F3.

## 11. Uso de IA

El código y los documentos se construyeron con asistencia de IA bajo
especificación del equipo. Cada integrante revisó, ejecutó y verificó lo que
presenta. La declaración completa se incluye en el informe SEM-03.

## Anexo — Índice de capturas

| Pantalla | Archivo |
|---|---|
| Login (1280) | `docs/week-03/evidence/rnf-02/rnf-02-login-1280.png` |
| Login (360) | `docs/week-03/evidence/rnf-02/rnf-02-login-360.png` |
| Búsqueda (1280) | `docs/week-03/evidence/rnf-02/rnf-02-buscar-1280.png` |
| Búsqueda (360) | `docs/week-03/evidence/rnf-02/rnf-02-buscar-360.png` |
| Confirmar reserva | `docs/week-03/evidence/rnf-02/rnf-02-confirmar-1280.png` |
| Comprobante QR | `docs/week-03/evidence/rnf-02/rnf-02-qr-1280.png` |
| Mis reservas | `docs/week-03/evidence/rnf-02/rnf-02-mis-reservas-1280.png` |
| Panel del bibliotecario | `docs/week-03/evidence/rnf-02/rnf-02-bibliotecario-1280.png` |
| Tercera reserva rechazada | `docs/week-03/evidence/CP-03.png` |
| QR inválido y duplicado | `docs/week-03/evidence/CP-04.png` |
| Devolución tardía | `docs/week-03/evidence/CP-06.png` |
