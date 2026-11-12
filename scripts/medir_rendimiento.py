#!/usr/bin/env python3
"""Mide 20 reservas + generación de QR a nivel de servicio.

Cubre: RNF-01 (medición inicial; la formal se hace en S4).
Uso: .venv/bin/python scripts/medir_rendimiento.py
"""
import os
import sys
import time
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ.setdefault("DEMO_MODE", "1")

import django  # noqa: E402

django.setup()

from reservas import services  # noqa: E402
from reservas.models import Reserva, Recurso, Usuario  # noqa: E402

N = 20
BLOQUE = "10:00-11:00"


def main():
    usuario, _ = Usuario.objects.get_or_create(
        username="medicion@example.com",
        defaults={
            "email": "medicion@example.com",
            "first_name": "Medición",
            "last_name": "Local",
            "rol": Usuario.Rol.SOLICITANTE,
        },
    )
    recurso = Recurso.objects.get(nombre="Sala 3")
    base = services.hoy() + timedelta(days=1)
    Reserva.objects.filter(usuario=usuario).delete()

    tiempos = []
    for i in range(N):
        fecha = base
        inicio = time.perf_counter()
        reserva = services.crear_reserva(usuario, recurso, fecha, BLOQUE)
        services.qr_base64(reserva.qr.codigo)
        tiempos.append((time.perf_counter() - inicio) * 1000)
        reserva.delete()

    promedio = sum(tiempos) / len(tiempos)
    print(f"Peticiones: {N}")
    print(f"Promedio: {promedio:.1f} ms")
    print(f"Máximo:   {max(tiempos):.1f} ms")
    print(f"Mínimo:   {min(tiempos):.1f} ms")
    print("Nota: medición local del servicio + QR; la medición HTTP formal se hace en S4.")

    Reserva.objects.filter(usuario=usuario).delete()
    usuario.delete()


if __name__ == "__main__":
    main()
