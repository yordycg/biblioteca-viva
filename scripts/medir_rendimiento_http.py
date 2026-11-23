#!/usr/bin/env python3
"""Mide el flujo reserva + QR a nivel HTTP real (RNF-01).

Hace 20 peticiones HTTP contra el servidor local, cada una iniciando sesión y
confirmando una reserva distinta, y registra promedio, maximo y p95. Escribe el
resultado en docs/evidence/CP-08.txt para usarlo como evidencia del caso.

Uso (con el servidor en marcha):
    .venv/bin/python scripts/medir_rendimiento_http.py [URL] [N]
"""
import http.cookiejar
import re
import statistics
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000").rstrip("/")
N = int(sys.argv[2]) if len(sys.argv) > 2 else 20
SALIDA = Path(__file__).resolve().parents[1] / "docs" / "evidence" / "CP-08.txt"
CLAVE = "demo1234"
USUARIOS = ["estudiante1@virginiogomez.cl", "estudiante2@virginiogomez.cl"]
BLOQUES = ["10:00-11:00", "12:00-13:00", "15:00-16:00", "16:00-17:00"]
# Las salas se descubren desde la propia busqueda: los IDs dependen del seed.


def cliente():
    jar = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar)), jar


def csrf(html):
    m = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html)
    return m.group(1) if m else ""


def get(opener, ruta):
    with opener.open(BASE + ruta, timeout=30) as r:
        return r.read().decode()


def post(opener, ruta, datos, referer):
    cuerpo = urllib.parse.urlencode(datos).encode()
    req = urllib.request.Request(
        BASE + ruta,
        data=cuerpo,
        headers={"Referer": BASE + referer, "Content-Type": "application/x-www-form-urlencoded"},
    )
    with opener.open(req, timeout=30) as r:
        return r.read().decode()


def sesion(correo):
    opener, _ = cliente()
    html = get(opener, "/login/")
    post(opener, "/login/", {
        "csrfmiddlewaretoken": csrf(html),
        "username": correo,
        "password": CLAVE,
    }, "/login/")
    return opener


def main():
    tiempos = []
    detalle = []
    hoy = date.today()
    i = 0
    intentos = 0
    while len(tiempos) < N and intentos < N * 3:
        intentos += 1
        correo = USUARIOS[i % 2]
        fecha = hoy + timedelta(days=(i // 4) % 7)
        bloque = BLOQUES[(i // 2) % 4]
        opener = sesion(correo)
        busqueda = get(
            opener,
            f"/buscar/?vista=recursos&filtrar=1&fecha={fecha.isoformat()}&bloque={bloque}",
        )
        salas = re.findall(r"/reservar/(\d+)/", busqueda)
        if len(salas) < 1:
            detalle.append(f"{i+1:02d} {correo} {fecha} {bloque}: sin recursos libres")
            i += 1
            continue
        sala = salas[0]
        pagina = get(opener, f"/reservar/{sala}/?fecha={fecha.isoformat()}&bloque={bloque}")
        inicio = time.perf_counter()
        html = post(
            opener,
            f"/reservar/{sala}/",
            {
                "csrfmiddlewaretoken": csrf(pagina),
                "fecha": fecha.isoformat(),
                "bloque": bloque,
            },
            f"/reservar/{sala}/",
        )
        ms = (time.perf_counter() - inicio) * 1000
        codigo = re.search(r"RSV-\d+", html)
        if not codigo:
            detalle.append(f"{i+1:02d} {correo} {fecha} {bloque}: sin QR")
            i += 1
            continue
        tiempos.append(ms)
        detalle.append(f"{i+1:02d} {correo} {fecha} {bloque} {codigo.group(0)}: {ms:.0f} ms")
        i += 1

    if not tiempos:
        sys.exit("ERROR: ninguna peticion creo una reserva")

    promedio = statistics.mean(tiempos)
    ordenados = sorted(tiempos)
    p95 = ordenados[max(0, int(len(ordenados) * 0.95) - 1)]
    lineas = [
        "CP-08 - Reserva y QR dentro de 1,5 s (RNF-01)",
        f"Servidor: {BASE}",
        f"Peticiones medidas: {len(tiempos)}",
        f"Promedio: {promedio:.0f} ms",
        f"Maximo: {max(tiempos):.0f} ms",
        f"p95: {p95:.0f} ms",
        f"Umbral: 1500 ms -> {'CUMPLE' if max(tiempos) < 1500 else 'NO CUMPLE'}",
        "",
        "Detalle:",
        *detalle,
    ]
    salida = "\n".join(lineas) + "\n"
    SALIDA.write_text(salida, encoding="utf-8")
    print(salida)
    return 0 if max(tiempos) < 1500 else 1


if __name__ == "__main__":
    sys.exit(main())
