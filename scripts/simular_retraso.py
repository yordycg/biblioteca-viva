#!/usr/bin/env python3
"""Fuerza una devolución tardía y muestra la sanción de 7 días.

Cubre: RF-07.
Uso: .venv/bin/python scripts/simular_retraso.py
"""
import os
import sys
from datetime import date, datetime, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ.setdefault("DEMO_MODE", "1")
os.environ.setdefault("DEMO_NOW", "2026-11-12T10:00:00")

import django  # noqa: E402

django.setup()

from django.utils import timezone  # noqa: E402

from reservas import services  # noqa: E402
from reservas.models import Reserva, Recurso, Usuario  # noqa: E402

FECHA = date(2026, 11, 12)
BLOQUE = "10:00-11:00"


def aware(hora):
    return timezone.make_aware(datetime.combine(FECHA, hora))


def main():
    usuario = Usuario.objects.get(username="estudiante1@example.com")
    recurso = Recurso.objects.get(nombre="Sala 3")
    Reserva.objects.filter(recurso=recurso, fecha=FECHA, bloque=BLOQUE).delete()

    reserva = services.crear_reserva(usuario, recurso, FECHA, BLOQUE)
    print("Reserva:", reserva.codigo)

    reserva = services.validar_inicio(reserva.codigo, aware(time(10, 5)))
    print("Estado tras la entrega:", reserva.get_estado_display())

    reserva, sancion = services.registrar_devolucion(reserva.codigo, aware(time(11, 1)))
    print("Estado tras la devolución:", reserva.get_estado_display())
    if sancion:
        print("Sanción aplicada:", sancion.inicio, "→", sancion.fin)
        print("Usuario sancionado hasta:", reserva.usuario.sancionado_hasta)
    else:
        print("No se aplicó sanción (revisar el escenario).")


if __name__ == "__main__":
    main()
