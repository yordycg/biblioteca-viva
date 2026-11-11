"""Pruebas automáticas de las reglas principales (RF-01, RF-03, RF-06, RF-07)."""
from datetime import date, datetime, time

from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.utils import timezone

from . import services
from .models import QR, Recurso, Reserva, Sancion, Usuario


class ReglasDeNegocioTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="u@example.com",
            email="u@example.com",
            password="demo1234",
            rol=Usuario.Rol.SOLICITANTE,
        )
        self.otro = Usuario.objects.create_user(
            username="otro@example.com",
            email="otro@example.com",
            password="demo1234",
            rol=Usuario.Rol.SOLICITANTE,
        )
        self.sala = Recurso.objects.create(
            nombre="Sala 3", tipo=Recurso.Tipo.SALA, capacidad=8
        )
        self.sala2 = Recurso.objects.create(
            nombre="Sala 1", tipo=Recurso.Tipo.SALA, capacidad=4
        )
        self.fecha = date(2026, 11, 10)

    def test_crear_reserva_genera_qr(self):
        reserva = services.crear_reserva(
            self.usuario, self.sala, self.fecha, "10:00-11:00"
        )
        self.assertEqual(reserva.estado, Reserva.Estado.RESERVADA)
        self.assertTrue(QR.objects.filter(reserva=reserva).exists())
        self.assertEqual(reserva.qr.codigo, reserva.codigo)

    def test_rf06_rechaza_tercera_reserva(self):
        services.crear_reserva(self.usuario, self.sala, self.fecha, "10:00-11:00")
        services.crear_reserva(self.usuario, self.sala2, self.fecha, "15:00-16:00")
        with self.assertRaises(ValidationError):
            services.crear_reserva(
                self.usuario, self.sala, self.fecha, "11:00-12:00"
            )

    def test_busqueda_excluye_recurso_ocupado(self):
        services.crear_reserva(self.otro, self.sala, self.fecha, "10:00-11:00")
        disponibles = list(
            services.recursos_disponibles("SALA", self.fecha, "10:00-11:00")
        )
        self.assertNotIn(self.sala, disponibles)
        self.assertIn(self.sala2, disponibles)

    @override_settings(DEMO_MODE=True)
    def test_qr_duplicado_se_rechaza(self):
        reserva = services.crear_reserva(
            self.usuario, self.sala, self.fecha, "10:00-11:00"
        )
        momento = timezone.make_aware(
            datetime.combine(self.fecha, time(10, 5))
        )
        services.validar_inicio(reserva.codigo, momento)
        with self.assertRaises(ValidationError):
            services.validar_inicio(reserva.codigo, momento)

    @override_settings(DEMO_MODE=True)
    def test_devolucion_tardia_aplica_sancion(self):
        reserva = services.crear_reserva(
            self.usuario, self.sala, self.fecha, "10:00-11:00"
        )
        inicio = timezone.make_aware(datetime.combine(self.fecha, time(10, 5)))
        tarde = timezone.make_aware(datetime.combine(self.fecha, time(11, 1)))
        services.validar_inicio(reserva.codigo, inicio)
        reserva, sancion = services.registrar_devolucion(reserva.codigo, tarde)
        self.assertEqual(reserva.estado, Reserva.Estado.FINALIZADA)
        self.assertIsNotNone(sancion)
        self.assertTrue(Sancion.objects.filter(reserva=reserva).exists())
        self.usuario.refresh_from_db()
        self.assertIsNotNone(self.usuario.sancionado_hasta)

    def test_cupo_diario_calculado(self):
        services.crear_reserva(self.usuario, self.sala, self.fecha, "10:00-11:00")
        cupo = services.cupo_diario(self.usuario, self.fecha)
        self.assertEqual(cupo["usadas"], 1)
        self.assertEqual(cupo["max"], services.MAX_RESERVAS_DIA)
        self.assertEqual(cupo["restantes"], 1)
        self.assertEqual(cupo["porcentaje"], 50)


class InterfazTests(TestCase):
    """Comprobaciones de las vistas que sostienen la interfaz (RNF-02)."""

    def setUp(self):
        self.hoy = timezone.localdate()
        self.estudiante = Usuario.objects.create_user(
            username="e@example.com",
            email="e@example.com",
            password="demo1234",
            rol=Usuario.Rol.SOLICITANTE,
        )
        self.bibliotecario = Usuario.objects.create_user(
            username="b@example.com",
            email="b@example.com",
            password="demo1234",
            rol=Usuario.Rol.BIBLIOTECARIO,
        )
        self.sala = Recurso.objects.create(
            nombre="Sala 3",
            tipo=Recurso.Tipo.SALA,
            ubicacion="Piso 1",
            capacidad=8,
        )
        self.reserva = services.crear_reserva(
            self.estudiante, self.sala, self.hoy, "10:00-11:00"
        )

    def test_busqueda_muestra_cupo_diario(self):
        self.client.force_login(self.estudiante)
        respuesta = self.client.get("/buscar/")
        self.assertContains(respuesta, "1/2")
        self.assertContains(respuesta, "1 reserva disponible")

    def test_panel_bibliotecario_lista_reservas_del_dia(self):
        self.client.force_login(self.bibliotecario)
        respuesta = self.client.get("/bibliotecario/")
        self.assertContains(respuesta, self.reserva.codigo)
        self.assertContains(respuesta, "Reservas del día")
        self.assertContains(respuesta, "Sala 3")

    def test_estudiante_no_accede_al_panel(self):
        self.client.force_login(self.estudiante)
        respuesta = self.client.get("/bibliotecario/")
        self.assertEqual(respuesta.status_code, 403)

    def test_qr_muestra_codigo_y_estado(self):
        self.client.force_login(self.estudiante)
        respuesta = self.client.get(f"/reserva/{self.reserva.pk}/qr/")
        self.assertContains(respuesta, self.reserva.codigo)
        self.assertContains(respuesta, "Comprobante de reserva")
        self.assertContains(respuesta, "Reservada")
