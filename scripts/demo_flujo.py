#!/usr/bin/env python3
"""Recorre el flujo completo sin usar el navegador.

Cubre: RF-01 a RF-07.
Uso: .venv/bin/python scripts/demo_flujo.py
"""
import os
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ.setdefault("DEMO_MODE", "1")
os.environ.setdefault("DEMO_NOW", "2026-11-11T10:00:00")

import django  # noqa: E402

django.setup()

from django.utils import timezone  # noqa: E402

from reservas import services  # noqa: E402
from reservas.models import Reserva, Recurso, Usuario  # noqa: E402

FECHA = date(2026, 11, 11)
BLOQUE = "10:00-11:00"


def aware(hora):
    return timezone.make_aware(datetime.combine(FECHA, hora))


def main():
    usuario = Usuario.objects.get(username="estudiante1@example.com")
    recurso = Recurso.objects.get(nombre="Sala 3")
    Reserva.objects.filter(recurso=recurso, fecha=FECHA, bloque=BLOQUE).delete()

    print("1. Búsqueda de recursos libres")
    print("   Disponibles:", [r.nombre for r in services.recursos_disponibles("SALA", FECHA, BLOQUE)])

    print("2. Reserva + QR")
    reserva = services.crear_reserva(usuario, recurso, FECHA, BLOQUE)
    print("   Reserva:", reserva.codigo, "| estado:", reserva.get_estado_display())

    print("3. Validación del QR")
    reserva = services.validar_inicio(reserva.codigo, aware(datetime.min.time().replace(hour=10, minute=5)))
    print("   Estado:", reserva.get_estado_display())

    print("4. Devolución dentro del bloque")
    reserva, sancion = services.registrar_devolucion(
        reserva.codigo, aware(datetime.min.time().replace(hour=10, minute=45))
    )
    print("   Estado:", reserva.get_estado_display(), "| sanción:", sancion)
    print("Flujo completo OK.")


if __name__ == "__main__":
    main()
