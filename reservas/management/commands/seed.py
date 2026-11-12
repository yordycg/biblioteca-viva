"""
Comando de datos semilla ficticios.

Uso:
    python manage.py seed
    python manage.py seed --reset
"""
from datetime import date

from django.core.management.base import BaseCommand

from reservas.models import Libro, QR, Recurso, Reserva, Sancion, Usuario

PASSWORD = "demo1234"
FECHA_DEMO = date(2026, 11, 10)


class Command(BaseCommand):
    help = "Carga usuarios, recursos y una reserva ficticia para la demo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Borra reservas, QR, sanciones y recursos antes de cargar.",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            Sancion.objects.all().delete()
            QR.objects.all().delete()
            Reserva.objects.all().delete()
            Recurso.objects.all().delete()
            Usuario.objects.exclude(is_superuser=True).delete()
            self.stdout.write("Datos anteriores eliminados.")

        usuarios = [
            ("estudiante1@example.com", "Estudiante", "1", Usuario.Rol.SOLICITANTE),
            ("estudiante2@example.com", "Estudiante", "2", Usuario.Rol.SOLICITANTE),
            ("bibliotecario1@example.com", "Bibliotecario", "1", Usuario.Rol.BIBLIOTECARIO),
        ]
        for username, first_name, last_name, rol in usuarios:
            usuario, created = Usuario.objects.get_or_create(
                username=username,
                defaults={
                    "email": username,
                    "first_name": first_name,
                    "last_name": last_name,
                    "rol": rol,
                },
            )
            if created:
                usuario.set_password(PASSWORD)
                usuario.save()
            else:
                usuario.email = username
                usuario.first_name = first_name
                usuario.last_name = last_name
                usuario.rol = rol
                usuario.save(update_fields=["email", "first_name", "last_name", "rol"])
            self.stdout.write(f"Usuario: {username} ({rol})")

        recursos = [
            ("Sala 3", Recurso.Tipo.SALA, "Piso 1", 8, ""),
            ("Sala 1", Recurso.Tipo.SALA, "Piso 1", 4, ""),
            ("Proyector Epson", Recurso.Tipo.EQUIPO, "Piso 1", None, "eq-014"),
            ("Notebook Dell", Recurso.Tipo.EQUIPO, "Piso 1", None, "eq-002"),
        ]
        for nombre, tipo, ubicacion, capacidad, codigo in recursos:
            recurso, created = Recurso.objects.get_or_create(
                nombre=nombre,
                defaults={
                    "tipo": tipo,
                    "ubicacion": ubicacion,
                    "capacidad": capacidad,
                    "codigo": codigo,
                },
            )
            if not created:
                recurso.tipo = tipo
                recurso.ubicacion = ubicacion
                recurso.capacidad = capacidad
                recurso.codigo = codigo
                recurso.save(update_fields=["tipo", "ubicacion", "capacidad", "codigo"])
            self.stdout.write(f"Recurso: {nombre}")

        libros = [
            {
                "nombre": "Don Quijote de la Mancha",
                "autor": "Miguel de Cervantes",
                "editorial": "Ediciones BibliotecaViva",
                "anio": 1605,
                "isbn": "978-956-00-0001-1",
                "genero": "Novela",
                "paginas": 863,
                "ubicacion": "Estante A-1",
                "codigo": "lib-001",
                "portada": "reservas/covers/quijote.svg",
                "sinopsis": "Las aventuras de Alonso Quijano y su escudero Sancho Panza en su viaje por La Mancha.",
            },
            {
                "nombre": "Martín Fierro",
                "autor": "José Hernández",
                "editorial": "Ediciones BibliotecaViva",
                "anio": 1872,
                "isbn": "978-956-00-0002-8",
                "genero": "Poesía",
                "paginas": 240,
                "ubicacion": "Estante A-2",
                "codigo": "lib-002",
                "portada": "reservas/covers/martin-fierro.svg",
                "sinopsis": "Poema gauchesco sobre la vida del gaucho Martín Fierro en la pampa argentina.",
            },
            {
                "nombre": "La Araucana",
                "autor": "Alonso de Ercilla",
                "editorial": "Ediciones BibliotecaViva",
                "anio": 1569,
                "isbn": "978-956-00-0003-5",
                "genero": "Poesía épica",
                "paginas": 320,
                "ubicacion": "Estante A-3",
                "codigo": "lib-003",
                "portada": "reservas/covers/araucana.svg",
                "sinopsis": "Epopeya en verso sobre la conquista de Chile y la resistencia del pueblo mapuche.",
            },
            {
                "nombre": "Veinte mil leguas de viaje submarino",
                "autor": "Julio Verne",
                "editorial": "Ediciones BibliotecaViva",
                "anio": 1870,
                "isbn": "978-956-00-0004-2",
                "genero": "Aventura",
                "paginas": 384,
                "ubicacion": "Estante B-1",
                "codigo": "lib-004",
                "portada": "reservas/covers/veinte-mil-leguas.svg",
                "sinopsis": "El capitán Nemo y el Nautilus recorren los océanos en una expedición científica y fantástica.",
            },
            {
                "nombre": "La metamorfosis",
                "autor": "Franz Kafka",
                "editorial": "Ediciones BibliotecaViva",
                "anio": 1915,
                "isbn": "978-956-00-0005-9",
                "genero": "Novela",
                "paginas": 120,
                "ubicacion": "Estante B-2",
                "codigo": "lib-005",
                "portada": "reservas/covers/metamorfosis.svg",
                "sinopsis": "Gregor Samsa despierta transformado en un insecto y su familia enfrenta la extrañeza.",
            },
            {
                "nombre": "Frankenstein",
                "autor": "Mary Shelley",
                "editorial": "Ediciones BibliotecaViva",
                "anio": 1818,
                "isbn": "978-956-00-0006-6",
                "genero": "Terror",
                "paginas": 280,
                "ubicacion": "Estante B-3",
                "codigo": "lib-006",
                "portada": "reservas/covers/frankenstein.svg",
                "sinopsis": "El doctor Victor Frankenstein da vida a una criatura y desata consecuencias que no puede controlar.",
            },
        ]
        for datos in libros:
            nombre = datos["nombre"]
            libro, created = Libro.objects.get_or_create(
                nombre=nombre, defaults=datos
            )
            if not created:
                for campo, valor in datos.items():
                    setattr(libro, campo, valor)
                libro.save()
            self.stdout.write(f"Libro: {nombre}")

        estudiante2 = Usuario.objects.get(username="estudiante2@example.com")
        sala1 = Recurso.objects.get(nombre="Sala 1")
        reserva, created = Reserva.objects.get_or_create(
            recurso=sala1,
            fecha=FECHA_DEMO,
            bloque="10:00-11:00",
            defaults={"usuario": estudiante2},
        )
        if created:
            QR.objects.create(reserva=reserva, codigo=reserva.codigo)
            self.stdout.write(f"Reserva de ejemplo: {reserva.codigo} (Sala 1)")
        else:
            self.stdout.write(f"Reserva de ejemplo ya existente: {reserva.codigo}")

        self.stdout.write(self.style.SUCCESS("Seed listo."))
        self.stdout.write(f"Contraseña de todos los usuarios: {PASSWORD}")
