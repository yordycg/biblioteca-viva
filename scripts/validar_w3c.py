#!/usr/bin/env python3
"""Valida el HTML de las pantallas con el validador del W3C (Nu, vnu.jar).

Descarga el HTML real de cada pantalla con una sesion valida y lo pasa por el
validador oficial para detectar errores de marcado (RNF-02: estandares y
compatibilidad).

Requisitos:
    - Servidor local en marcha.
    - `~/.local/opt/vnu.jar` y un JRE 17+ (`JAVA_HOME`).
    - Descarga del validador:
      https://github.com/validator/validator/releases/download/latest/vnu.jar

Uso:
    .venv/bin/python scripts/validar_w3c.py [URL]
"""
import http.cookiejar
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8001").rstrip("/")
SALIDA = Path(__file__).resolve().parents[1] / "docs" / "evidence" / "w3c"
VNU = Path.home() / ".local" / "opt" / "vnu.jar"
CLAVE = "demo1234"

PANTALLAS = [
    ("login", "/login/", None),
    ("buscar", "/buscar/", "estudiante1@virginiogomez.cl"),
    ("libros", "/libros/", "estudiante1@virginiogomez.cl"),
    ("mis-reservas", "/mis-reservas/", "estudiante1@virginiogomez.cl"),
    ("bibliotecario", "/bibliotecario/", "bibliotecario1@virginiogomez.cl"),
]


def csrf(html):
    m = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html)
    return m.group(1) if m else ""


def abrir(correo):
    """Devuelve un opener con sesion iniciada (o anonimo si correo es None)."""
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    if not correo:
        return opener
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
    return opener


def java():
    """Ruta al ejecutable de Java: JAVA_HOME si existe, si no el del PATH."""
    casa = os.environ.get("JAVA_HOME")
    if casa:
        return str(Path(casa) / "bin" / "java")
    return "java"


def validar(ruta, html):
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as tmp:
        tmp.write(html)
        archivo = tmp.name
    try:
        resultado = subprocess.run(
            [java(), "-jar", str(VNU), "--format", "json", "--stdout", archivo],
            capture_output=True, text=True, check=False,
        )
    finally:
        os.unlink(archivo)
    datos = json.loads(resultado.stdout or "{}")
    return datos.get("messages", [])


def main():
    if not VNU.exists():
        raise SystemExit(f"Falta {VNU}; descarga vnu.jar del repositorio del W3C.")
    SALIDA.mkdir(parents=True, exist_ok=True)
    resumen = []
    for nombre, ruta, usuario in PANTALLAS:
        opener = abrir(usuario)
        with opener.open(BASE + ruta) as r:
            html = r.read().decode()
        mensajes = validar(ruta, html)
        errores = [m for m in mensajes if m.get("type") == "error"]
        avisos = [m for m in mensajes if m.get("type") != "error"]
        (SALIDA / f"{nombre}.json").write_text(
            json.dumps(mensajes, indent=2, ensure_ascii=False)
        )
        resumen.append({"pantalla": nombre, "ruta": ruta, "errores": len(errores),
                        "avisos": len(avisos)})
        print(f"{nombre:14} errores: {len(errores):3}  avisos: {len(avisos):3}")
        for m in errores[:5]:
            print(f"   - {m.get('message')}")
    (SALIDA / "resumen.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False))
    total = sum(f["errores"] for f in resumen)
    print()
    print(f"Total de errores de marcado: {total}")


if __name__ == "__main__":
    main()
