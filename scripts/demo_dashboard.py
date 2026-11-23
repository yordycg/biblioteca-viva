#!/usr/bin/env python3
"""Carga datos ficticios para ver el potencial del panel del bibliotecario.

Cubre: RF-01, RF-04, RF-05, RF-07.
Uso: .venv/bin/python scripts/demo_dashboard.py
"""
import os
import sys
from datetime import time, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from django.db import transaction  # noqa: E402

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
    QR.objects.get_or_create(reserva=reserva, defaults={"codigo": reserva.codigo})
    return reserva


def main():
    hoy = services.hoy()
    ahora = services.ahora()
    bloques = [valor for valor, _ in services.bloques_disponibles(hoy)]
    if not bloques:
        print("Aviso: hoy no quedan bloques; se usan los del catálogo completo.")
        bloques = [valor for valor, _ in Reserva.BLOQUES]

    def bloque_de_ahora():
        """Bloque que está corriendo en este momento, si lo hay."""
        hora = services.ahora().time()
        for valor, _ in Reserva.BLOQUES:
            inicio, fin = valor.split("-")
            if time.fromisoformat(inicio) <= hora < time.fromisoformat(fin):
                return valor
        return None

    def bloque_libre(recurso, desde=0):
        """Primer bloque del día sin reserva para ese recurso.

        El seed deja una reserva propia en el primer bloque; el panel no puede
        reutilizar ese hueco porque la base exige un bloque único por recurso.
        Si el día ya no tiene bloques, se recorre la lista completa.
        """
        orden = bloques[desde:] + bloques[:desde]
        for bloque in orden:
            ocupado = Reserva.objects.filter(
                recurso=recurso, fecha=hoy, bloque=bloque
            ).exists()
            if not ocupado:
                return bloque
        return None

    def crear_en_bloque(usuario, recurso, estado, desde=0):
        bloque = bloque_libre(recurso, desde)
        if not bloque:
            print(f"Aviso: {recurso.nombre} ya no tiene bloques libres.")
            return None
        return crear_reserva(usuario, recurso, estado, bloque)

    with transaction.atomic():
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

        # Entregas pendientes, en uso, finalizada y cancelada: el panel muestra
        # los cuatro estados sin pisar los bloques que ya dejó el seed.
        sala = crear_en_bloque(ana, sala3, Reserva.Estado.RESERVADA, 0)
        proyector_reserva = crear_en_bloque(
            luis, proyector, Reserva.Estado.RESERVADA, 2
        )
        # Una finalizada de primera hora y una en uso del bloque actual: así la
        # línea de tiempo del día muestra actividad, no solo la última franja.
        primera = [valor for valor, _ in Reserva.BLOQUES][0]
        crear_reserva(carla, notebook, Reserva.Estado.FINALIZADA, primera)
        crear_reserva(
            carla,
            sala1,
            Reserva.Estado.EN_USO,
            bloque_de_ahora() or bloque_libre(sala1, 0) or "21:00-22:00",
        )
        crear_en_bloque(ana, proyector, Reserva.Estado.CANCELADA, 4)

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

    activas = Reserva.objects.filter(fecha=hoy).count()
    print(f"Datos de panel cargados para {hoy}: {activas} reservas del día.")
    codigos = [r.codigo for r in (sala, proyector_reserva) if r]
    print(f"Entregas pendientes: {', '.join(codigos) or 'ninguna'}.")
    print("También hay una en uso, una finalizada, una cancelada, un préstamo")
    print("pendiente, uno que vence hoy, uno vencido y una sanción activa.")


if __name__ == "__main__":
    main()
