#!/usr/bin/env python3
"""Carga datos ficticios para ver el potencial del panel del bibliotecario.

Cubre: RF-01, RF-04, RF-05, RF-07.
Uso: .venv/bin/python scripts/demo_dashboard.py
"""
import os
import sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from django.utils import timezone  # noqa: E402

from reservas import services  # noqa: E402
from reservas.models import QR, Libro, Recurso, Reserva, Sancion, Usuario  # noqa: E402

PASSWORD = "demo1234"
DEMO_USERS = [
    ("ana.perez@example.com", "Ana", "Pérez"),
    ("luis.soto@example.com", "Luis", "Soto"),
    ("carla.rojas@example.com", "Carla", "Rojas"),
]


def crear_reserva(usuario, recurso, estado, bloque="", fecha=None, vencimiento=None):
    reserva = Reserva.objects.create(
        usuario=usuario,
        recurso=recurso,
        fecha=fecha or services.hoy(),
        modalidad=(
            Reserva.Modalidad.PRESTAMO if not bloque else Reserva.Modalidad.BLOQUE
        ),
        bloque=bloque,
        fecha_vencimiento=vencimiento,
        estado=estado,
        iniciada_en=services.ahora() if estado == Reserva.Estado.EN_USO else None,
        finalizada_en=(
            services.ahora() - timedelta(hours=1)
            if estado == Reserva.Estado.FINALIZADA
            else None
        ),
    )
    QR.objects.create(reserva=reserva, codigo=reserva.codigo)
    return reserva


def main():
    hoy = services.hoy()
    ahora = services.ahora()
    bloques = services.bloques_disponibles(hoy)
    if not bloques:
        print("Aviso: hoy no quedan bloques; se usa el último del día como referencia.")
        bloques = list(Reserva.BLOQUES)[-1:]
    bloque_a = bloques[0][0]
    bloque_b = bloques[min(1, len(bloques) - 1)][0]

    usuarios = []
    for username, nombre, apellido in DEMO_USERS:
        usuario, creado = Usuario.objects.get_or_create(
            username=username,
            defaults={
                "email": username,
                "first_name": nombre,
                "last_name": apellido,
                "rol": Usuario.Rol.SOLICITANTE,
            },
        )
        if creado:
            usuario.set_password(PASSWORD)
            usuario.save()
        usuario.sancionado_hasta = None
        usuario.save(update_fields=["sancionado_hasta"])
        usuarios.append(usuario)

    ana, luis, carla = usuarios
    Reserva.objects.filter(usuario__in=usuarios).delete()
    Sancion.objects.filter(usuario__in=usuarios).delete()

    sala3 = Recurso.objects.get(nombre="Sala 3")
    sala1 = Recurso.objects.get(nombre="Sala 1")
    proyector = Recurso.objects.get(nombre="Proyector Epson")
    notebook = Recurso.objects.get(nombre="Notebook Dell")
    quijote = Libro.objects.get(nombre="Don Quijote de la Mancha")
    martin = Libro.objects.get(nombre="Martín Fierro")
    araucana = Libro.objects.get(nombre="La Araucana")

    # Próximas entregas por bloque (diferentes tipos de recurso).
    sala = crear_reserva(ana, sala3, Reserva.Estado.RESERVADA, bloque_a)
    proyector_reserva = crear_reserva(
        luis, proyector, Reserva.Estado.RESERVADA, bloque_b
    )
    crear_reserva(carla, sala1, Reserva.Estado.EN_USO, bloque_a)
    crear_reserva(carla, notebook, Reserva.Estado.FINALIZADA, bloque_b)

    # Préstamos de libros: pendiente, vence hoy y vencido.
    crear_reserva(
        carla,
        araucana,
        Reserva.Estado.RESERVADA,
        fecha=hoy,
        vencimiento=hoy + timedelta(days=7),
    )
    crear_reserva(
        ana,
        quijote,
        Reserva.Estado.EN_USO,
        fecha=hoy - timedelta(days=7),
        vencimiento=hoy,
    )
    crear_reserva(
        luis,
        martin,
        Reserva.Estado.EN_USO,
        fecha=hoy - timedelta(days=10),
        vencimiento=hoy - timedelta(days=2),
    )

    fin_sancion = ahora + timedelta(days=6)
    Sancion.objects.create(
        usuario=luis,
        inicio=ahora - timedelta(days=1),
        fin=fin_sancion,
        motivo="Devolución tardía",
    )
    luis.sancionado_hasta = fin_sancion
    luis.save(update_fields=["sancionado_hasta"])

    print(f"Datos de panel cargados para {hoy} · bloques {bloque_a} y {bloque_b}.")
    print(f"Entregas: {sala.codigo}, {proyector_reserva.codigo}")
    print("También hay un préstamo pendiente, uno que vence hoy y uno vencido.")


if __name__ == "__main__":
    main()
