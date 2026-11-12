"""Pruebas automáticas de las reglas principales (RF-01, RF-03, RF-06, RF-07)."""
from datetime import date, datetime, time, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.utils import timezone

from . import services
from .forms import BusquedaForm
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


class FechaMinimaTests(TestCase):
    """La búsqueda y la reserva no aceptan fechas pasadas (RF-01, RF-02)."""

    def setUp(self):
        self.ayer = timezone.localdate() - timedelta(days=1)

    def test_busqueda_rechaza_fecha_pasada(self):
        form = BusquedaForm(
            {
                "tipo": Recurso.Tipo.SALA,
                "fecha": self.ayer,
                "bloque": "10:00-11:00",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("anterior a hoy", form.errors["fecha"][0])

    def test_busqueda_acepta_hoy(self):
        form = BusquedaForm(
            {
                "tipo": Recurso.Tipo.SALA,
                "fecha": timezone.localdate(),
                "bloque": "10:00-11:00",
            }
        )
        self.assertTrue(form.is_valid())

    def test_formulario_expone_fecha_minima(self):
        form = BusquedaForm()
        self.assertEqual(
            form.fields["fecha"].widget.attrs["min"],
            timezone.localdate().isoformat(),
        )


class InventarioTests(TestCase):
    """Estado agregado del inventario para el panel del bibliotecario."""

    def setUp(self):
        self.hoy = timezone.localdate()
        self.usuario = Usuario.objects.create_user(
            username="inv@example.com",
            email="inv@example.com",
            password="demo1234",
            rol=Usuario.Rol.SOLICITANTE,
        )
        self.sala_libre = Recurso.objects.create(
            nombre="Sala 1", tipo=Recurso.Tipo.SALA
        )
        self.sala_reservada = Recurso.objects.create(
            nombre="Sala 3", tipo=Recurso.Tipo.SALA
        )
        self.equipo_en_uso = Recurso.objects.create(
            nombre="Proyector Epson", tipo=Recurso.Tipo.EQUIPO
        )
        self.equipo_off = Recurso.objects.create(
            nombre="Notebook Dell",
            tipo=Recurso.Tipo.EQUIPO,
            estado=Recurso.Estado.NO_DISPONIBLE,
        )
        services.crear_reserva(
            self.usuario, self.sala_reservada, self.hoy, "10:00-11:00"
        )
        Reserva.objects.create(
            usuario=self.usuario,
            recurso=self.equipo_en_uso,
            fecha=self.hoy,
            bloque="11:00-12:00",
            estado=Reserva.Estado.EN_USO,
        )

    def test_resumen_inventario(self):
        resumen = services.estado_inventario(self.hoy)["resumen"]
        self.assertEqual(resumen["total"], 4)
        self.assertEqual(resumen["disponibles"], 1)
        self.assertEqual(resumen["reservados"], 1)
        self.assertEqual(resumen["en_uso"], 1)
        self.assertEqual(resumen["no_disponibles"], 1)
        self.assertEqual(resumen["ocupados"], 2)
        self.assertEqual(resumen["porcentaje"], 50)

    def test_estado_por_bloque(self):
        inventario = services.estado_inventario(self.hoy)
        fila = next(
            f for f in inventario["filas"] if f["recurso"] == self.sala_reservada
        )
        estados = {b["clave"]: b["estado"] for b in fila["bloques"]}
        self.assertEqual(estados["10:00-11:00"], "RESERVADO")
        self.assertEqual(estados["11:00-12:00"], "DISPONIBLE")

    def test_resumen_por_tipo(self):
        inventario = services.estado_inventario(self.hoy)
        tipos = {t["tipo"]: t for t in inventario["por_tipo"]}
        self.assertEqual(tipos[Recurso.Tipo.SALA]["total"], 2)
        self.assertEqual(tipos[Recurso.Tipo.EQUIPO]["no_disponibles"], 1)


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

    def test_busqueda_muestra_error_para_fecha_pasada(self):
        self.client.force_login(self.estudiante)
        ayer = timezone.localdate() - timedelta(days=1)
        respuesta = self.client.get(
            "/buscar/",
            {
                "tipo": Recurso.Tipo.SALA,
                "fecha": ayer.isoformat(),
                "bloque": "10:00-11:00",
            },
        )
        self.assertContains(respuesta, "no puede ser anterior a hoy")
        self.assertIsNone(respuesta.context["resultados"])

    def test_confirmar_rechaza_fecha_pasada(self):
        self.client.force_login(self.estudiante)
        ayer = timezone.localdate() - timedelta(days=1)
        antes = Reserva.objects.count()
        respuesta = self.client.post(
            f"/reservar/{self.sala.pk}/",
            {"fecha": ayer.isoformat(), "bloque": "10:00-11:00"},
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "no puede ser anterior a hoy")
        self.assertEqual(Reserva.objects.count(), antes)

    def test_busqueda_expone_fecha_minima(self):
        self.client.force_login(self.estudiante)
        respuesta = self.client.get("/buscar/")
        self.assertContains(
            respuesta, f'min="{timezone.localdate().isoformat()}"'
        )

    def test_panel_bibliotecario_lista_reservas_del_dia(self):
        self.client.force_login(self.bibliotecario)
        respuesta = self.client.get("/bibliotecario/")
        self.assertContains(respuesta, self.reserva.codigo)
        self.assertContains(respuesta, "Reservas del día")
        self.assertContains(respuesta, "Sala 3")

    def test_panel_muestra_estado_del_inventario(self):
        self.client.force_login(self.bibliotecario)
        respuesta = self.client.get("/bibliotecario/")
        self.assertContains(respuesta, "Estado del inventario")
        self.assertContains(respuesta, "Disponibles hoy")
        self.assertContains(respuesta, "Ocupación del día")
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

    def test_login_muestra_logo_institucional(self):
        respuesta = self.client.get("/login/")
        self.assertContains(respuesta, "reservas/img/ipvg-logo.png")

    def test_login_no_expone_credenciales_de_demo(self):
        respuesta = self.client.get("/login/")
        self.assertNotContains(respuesta, "Credenciales de prueba")
        self.assertNotContains(respuesta, "estudiante1@example.com")
        self.assertNotContains(respuesta, "demo1234")

    def test_barra_superior_muestra_logo_institucional(self):
        self.client.force_login(self.estudiante)
        respuesta = self.client.get("/buscar/")
        self.assertContains(respuesta, "reservas/img/ipvg-logo.png")
        self.assertContains(respuesta, "BibliotecaViva")

    def test_login_valido_redirige(self):
        respuesta = self.client.post(
            "/login/", {"username": "e@example.com", "password": "demo1234"}
        )
        self.assertRedirects(respuesta, "/", fetch_redirect_response=False)

    def test_login_invalido_muestra_error(self):
        respuesta = self.client.post(
            "/login/", {"username": "e@example.com", "password": "incorrecta"}
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Correo o contraseña incorrectos")

    def test_busqueda_muestra_aviso_de_sancion(self):
        self.estudiante.sancionado_hasta = timezone.now() + timedelta(days=7)
        self.estudiante.save(update_fields=["sancionado_hasta"])
        self.client.force_login(self.estudiante)
        respuesta = self.client.get("/buscar/")
        self.assertContains(respuesta, "Sanción vigente")
