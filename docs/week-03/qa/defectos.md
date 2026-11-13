# Bitácora de defectos — semana 3

> Registro de defectos encontrados al ejecutar los casos de prueba.
> Un defecto entra aquí **solo** si se reprodujo en la aplicación; si un caso se
> ejecutó y no falló, no se inventa un hallazgo: se anota «sin defectos» en el
> resumen de la ejecución.

## Cómo registrar

1. Asignar el siguiente ID libre: `DEF-01`, `DEF-02`, …
2. Escribir pasos reproducibles, con los datos exactos (usuario, recurso, fecha,
   bloque y código si aplica).
3. Severidad según el impacto, no según la molestia:
   - **Crítica:** bloquea el flujo principal o pierde datos.
   - **Alta:** una regla de negocio se cumple mal (RF-06, RF-07).
   - **Media:** mensaje o estado incorrecto que confunde, sin pérdida de datos.
   - **Baja:** texto, alineación o detalle visual.
4. Al corregir, enlazar el commit y **volver a ejecutar el caso** con los mismos
   datos. La columna «Re-prueba» solo se completa con esa nueva ejecución.

## Registro

| ID | Descripción | Pasos para reproducir | Severidad | Caso asociado | Responsable | Estado | Corrección (commit) | Re-prueba |
|---|---|---|---|---|---|---|---|---|
| — | Sin registros todavía | — | — | — | — | — | — | — |

## Resumen de ejecución

| Fecha | Casos ejecutados | Aprobados | Fallidos | Bloqueados | Ejecutado por |
|---|---|---|---|---|---|
| 2026-11-13 | 11 | 11 | 0 | 0 | Script local · Yordy Carmona |
