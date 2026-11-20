#!/usr/bin/env bash
# Ejecuta la prueba de carga con JMeter en tres niveles de concurrencia (RNF-01).
#
# Requisitos:
#   - Servidor en marcha (por ejemplo gunicorn en 127.0.0.1:8010).
#   - JMeter 5.6 y un JRE 17+ (JAVA_HOME).
#
# Uso:
#   scripts/carga/ejecutar_carga.sh [host] [puerto] [duración_segundos]
#
# Deja un JTL y un informe HTML por nivel en docs/evidence/rnf-01-estres/.
set -euo pipefail

HOST="${1:-127.0.0.1}"
PORT="${2:-8010}"
DURACION="${3:-60}"
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
SALIDA="$RAIZ/docs/evidence/rnf-01-estres"
JMETER="${JMETER:-$HOME/.local/opt/apache-jmeter-5.6.3/bin/jmeter}"
export JAVA_HOME="${JAVA_HOME:-$HOME/.local/opt/jdk-21.0.13+9}"

mkdir -p "$SALIDA"

for HILOS in 1 10 50; do
  DESTINO="$SALIDA/${HILOS}u"
  rm -rf "$DESTINO"
  mkdir -p "$DESTINO"
  echo "== $HILOS usuarios concurrentes, $DURACION s =="
  "$JMETER" -n \
    -t "$RAIZ/scripts/carga/consulta.jmx" \
    -Jhost="$HOST" -Jport="$PORT" \
    -Jthreads="$HILOS" -Jramp="$HILOS" -Jduration="$DURACION" \
    -Jcsv="$RAIZ/scripts/carga/usuarios.csv" \
    -l "$DESTINO/resultados.jtl" \
    -e -o "$DESTINO/informe" 2>&1 | grep -E "^summary =" | tail -1
done

echo "Listo: $SALIDA"
