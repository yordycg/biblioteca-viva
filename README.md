# BibliotecaViva — Sistema de Gestión y Reservas

Repositorio de la solución informática y documentación para la Evaluación 3 de Ingeniería de Software (IP Virginio Gómez).

## Estado actual

- **Semana 1:** ficha del proyecto, requisitos y plan de calidad.
- **Semana 2:** diseño y QA base (mockups, UML, checklist, matriz y 6 casos de prueba; 12 al cierre).
- **Semana 3 en adelante:** implementación del MVP de F1–F3, pruebas y cierre.

## Estructura del repositorio

- `docs/week-01/`: ficha, requisitos y plan de calidad.
- `docs/week-02/`: diseño y QA base (checklist, mockups, diagramas, matriz y casos).
- `src/`: código fuente de la aplicación (se incorpora en semana 3).
- `tests/`: pruebas de software.

## Documentación

- [`docs/week-01/01-ficha-proyecto.md`](docs/week-01/01-ficha-proyecto.md)
- [`docs/week-01/02-requisitos.md`](docs/week-01/02-requisitos.md)
- [`docs/week-01/03-plan-calidad.md`](docs/week-01/03-plan-calidad.md)
- [`docs/week-02/README.md`](docs/week-02/README.md)
- [`docs/week-02/checklist-diseno.md`](docs/week-02/checklist-diseno.md)
- [`docs/week-02/qa/matriz-trazabilidad.md`](docs/week-02/qa/matriz-trazabilidad.md)
- [`docs/week-02/qa/casos-prueba.md`](docs/week-02/qa/casos-prueba.md)

## Cómo ejecutar (cuando el MVP esté implementado)

```bash
npm install
npm start
```

La aplicación quedará disponible en `http://localhost:3000`. Hasta la semana 3 el repositorio contiene solo documentación y artefactos de diseño.

## Datos y seguridad

- Todos los datos son ficticios.
- No se incluyen credenciales, tokens ni datos personales reales.
- Las variables de entorno se documentan en `.env.example`.
