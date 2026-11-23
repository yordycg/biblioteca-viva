#!/usr/bin/env python3
"""Audita accesibilidad, buenas practicas y rendimiento con Lighthouse (RNF-02).

Inicia sesion con los usuarios ficticios del seed para poder auditar las
pantallas privadas y ejecuta Lighthouse en formato movil y escritorio sobre las
rutas indicadas. Deja un informe HTML y otro JSON por pantalla y formato en
docs/evidence/rnf-02/lighthouse/ y un resumen en consola.

Requisitos:
    - Servidor local en marcha (por ejemplo `python manage.py runserver 127.0.0.1:8001`).
    - Lighthouse disponible (`npx lighthouse@12`) y un Chromium para CHROME_PATH.

Uso:
    .venv/bin/python scripts/auditar_lighthouse.py [URL]
"""
import http.cookiejar
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8001").rstrip("/")
SALIDA = Path(__file__).resolve().parents[1] / "docs" / "evidence" / "rnf-02" / "lighthouse"
CLAVE = "demo1234"

# (nombre, ruta, usuario, categorias)
PANTALLAS = [
    ("buscar", "/buscar/", "estudiante1@virginiogomez.cl"),
    ("mis-reservas", "/mis-reservas/", "estudiante1@virginiogomez.cl"),
    ("bibliotecario", "/bibliotecario/", "bibliotecario1@virginiogomez.cl"),
]

CATEGORIAS = "accessibility,best-practices,performance,seo"
UMBRALES = {"accessibility": 90, "best-practices": 90}


def csrf(html):
    m = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html)
    return m.group(1) if m else ""


def sesion(correo):
    """Devuelve el valor de la cookie de sesion de Django para ese usuario."""
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    with opener.open(BASE + "/login/") as r:
        html = r.read().decode()
    cuerpo = urllib.parse.urlencode(
        {"csrfmiddlewaretoken": csrf(html), "username": correo, "password": CLAVE}
    ).encode()
    req = urllib.request.Request(
        BASE + "/login/",
        data=cuerpo,
        headers={"Referer": BASE + "/login/", "Content-Type": "application/x-www-form-urlencoded"},
    )
    opener.open(req).read()
    for cookie in jar:
        if cookie.name == "sessionid":
            return f"sessionid={cookie.value}"
    raise SystemExit(f"No se obtuvo sesion para {correo}")


def auditar(ruta, cookie, formato):
    carpeta = SALIDA / formato
    carpeta.mkdir(parents=True, exist_ok=True)
    nombre = ruta.strip("/").replace("/", "-") or "home"
    destino = carpeta / nombre
    extra = json.dumps({"Cookie": cookie})
    comando = [
        "npx", "--yes", "lighthouse@12", BASE + ruta,
        f"--only-categories={CATEGORIAS}",
        "--output=json", "--output=html",
        f"--output-path={destino}",
        f"--extra-headers={extra}",
        "--chrome-flags=--headless=new --no-sandbox --disable-dev-shm-usage",
        "--quiet",
    ]
    if formato == "desktop":
        comando.append("--preset=desktop")
    informe = destino.parent.joinpath(destino.name + ".report.json")
    # Lighthouse devuelve codigo 1 cuando una metrica no se pudo calcular; si el
    # informe existe se acepta, y si no, se repite una vez antes de fallar.
    for intento in (1, 2):
        resultado = subprocess.run(comando, capture_output=True, text=True)
        if informe.exists():
            break
        if intento == 2:
            raise SystemExit(
                f"Lighthouse fallo en {ruta} ({formato}):\n{resultado.stderr[-800:]}"
            )
    return json.loads(informe.read_text())


def puntajes(informe):
    return {
        clave: (round(valor["score"] * 100) if valor.get("score") is not None else None)
        for clave, valor in informe["categories"].items()
    }


def main():
    SESIONES = {}
    filas = []
    for nombre, ruta, usuario in PANTALLAS:
        SESIONES.setdefault(usuario, sesion(usuario))
        for formato in ("mobile", "desktop"):
            print(f"Auditando {nombre} ({formato})...", flush=True)
            datos = auditar(ruta, SESIONES[usuario], formato)
            filas.append((nombre, formato, puntajes(datos)))

    print()
    print(f"{'Pantalla':16} {'Formato':9} {'A11y':>5} {'BP':>5} {'Perf':>5} {'SEO':>5}")
    for nombre, formato, p in filas:
        print(
            f"{nombre:16} {formato:9} {p.get('accessibility', '-'):>5} "
            f"{p.get('best-practices', '-'):>5} {p.get('performance', '-'):>5} "
            f"{p.get('seo', '-'):>5}"
        )

    fallos = [
        (n, f, c, p[c])
        for n, f, p in filas
        for c in UMBRALES
        if p.get(c) is not None and p[c] < UMBRALES[c]
    ]
    resumen = {
        "fecha": __import__("datetime").date.today().isoformat(),
        "servidor": BASE,
        "umbral": UMBRALES,
        "filas": [
            {"pantalla": n, "formato": f, **p} for n, f, p in filas
        ],
        "bajo_umbral": [
            {"pantalla": n, "formato": f, "categoria": c, "puntaje": v}
            for n, f, c, v in fallos
        ],
    }
    (SALIDA / "resumen.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False))
    print()
    if fallos:
        print(f"Bajo umbral ({len(fallos)}):")
        for n, f, c, v in fallos:
            print(f"  - {n} / {f} / {c}: {v} < {UMBRALES[c]}")
    else:
        print("Sin hallazgos bajo el umbral de 90 en accesibilidad y buenas practicas.")


if __name__ == "__main__":
    main()
