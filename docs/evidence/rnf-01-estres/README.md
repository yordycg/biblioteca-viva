# RNF-01 · Prueba de carga con JMeter

## Método

- Herramienta: **Apache JMeter 5.6.3** (JRE 21), modo *non-GUI* (`jmeter -n`).
- Servidor: **gunicorn** con 2 workers sobre `127.0.0.1:8010` y SQLite (la base del
  proyecto, sin cambios).
- Plan: `scripts/carga/consulta.jmx` — cada hilo hace login, una búsqueda con
  filtros y una consulta a “Mis reservas”; aserciones de contenido en cada paso.
- Niveles: 1, 10 y 50 usuarios concurrentes, rampa igual al número de hilos,
  60 segundos por nivel, datos del seed (`scripts/carga/usuarios.csv`).
- Ejecución reproducible: `scripts/carga/ejecutar_carga.sh 127.0.0.1 8010 60`.

Los informes HTML completos están en `1u/informe/`, `10u/informe/` y
`50u/informe/`; las muestras crudas, en `resultados.jtl`.

## Resultados

| Usuarios | Muestras | Rendimiento | Promedio | p95 | p99 | Máximo | Errores |
|---|---|---|---|---|---|---|---|
| 1 | 962 | 16,0 req/s | 61 ms | 227 ms | 234 ms | 261 ms | 0 % |
| 10 | 1.683 | 27,9 req/s | 328 ms | 896 ms | 1.119 ms | 1.310 ms | 0 % |
| 50 | 1.672 | 27,4 req/s | 1.078 ms | 3.338 ms | 3.963 ms | 4.514 ms | 0 % |

## Lectura

- El sistema **no pierde peticiones**: 0 % de error en los tres niveles, con
  aserciones de contenido activas (un login fallido o una página vacía habría
  contado como error).
- El **techo de rendimiento** aparece entre 10 y 50 usuarios: el rendimiento se
  mantiene en torno a 27 req/s y la latencia crece 17 veces (61 ms → 1.068 ms de
  promedio). El límite lo impone la combinación de 2 workers y SQLite, no el
  código de la aplicación.
- **Conclusión para el umbral del RNF-01**: con hasta 10 usuarios concurrentes
  el p95 se mantiene por debajo de 1,5 s (896 ms). A 50 usuarios concurrentes el
  p95 lo supera (3,3 s). Es el punto de saturación declarado en el informe.

## Reserva simultánea (integridad de RF-02)

`scripts/carga/reserva-concurrente.jmx`: 10 hilos intentan reservar **el mismo
recurso, fecha y bloque** en el mismo instante.

| Intento | Reservas creadas | Errores HTTP | Resultado |
|---|---|---|---|
| 10 simultáneos | **1** (RSV-0435) | 0 | Las 9 restantes se rechazaron con mensaje; no hubo doble reserva |

Evidencia: `reserva-concurrente.jtl` en esta misma carpeta.
