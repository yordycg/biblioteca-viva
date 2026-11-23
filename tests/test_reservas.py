"""Fecha mínima, ventana de reserva y cancelación (RF-01, RF-02)."""
from datetime import date, datetime, time, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.utils import timezone

from reservas import services
from reservas.forms import BusquedaForm, ReservaForm
from reservas.models import Libro, QR, Recurso, Reserva, Sancion, Usuario

@override_settings(DEMO_MODE=True, DEMO_NOW="2026-11-12T09:00:00")
class FechaMinimaTests(TestCase):
    """La búsqueda y la reserva no aceptan fechas pasadas (RF-01, RF-02)."""

    def setUp(self):
        self.ayer = services.hoy() - timedelta(days=1)

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
                "fecha": services.hoy(),
                "bloque": "10:00-11:00",
            }
        )
        self.assertTrue(form.is_valid())

    def test_formulario_expone_fecha_minima(self):
        form = BusquedaForm()
        self.assertEqual(
            form.fields["fecha"].widget.attrs["min"],
            services.hoy().isoformat(),
        )


@override_settings(DEMO_MODE=True, DEMO_NOW="2026-11-12T10:50:00")
class VentanaReservaTests(TestCase):
    """Ventana de reserva: bloques futuros, antelación y horizonte."""

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="ventana@virginiogomez.cl",
            email="ventana@virginiogomez.cl",
            password="demo1234",
            rol=Usuario.Rol.SOLICITANTE,
        )
        self.sala = Recurso.objects.create(
            nombre="Sala 9", tipo=Recurso.Tipo.SALA
        )
        self.fecha = services.hoy()

    def test_bloques_disponibles_filtra_iniciados_y_sin_antelacion(self):
        valores = [valor for valor, _ in services.bloques_disponibles(self.fecha)]
        self.assertEqual(
            valores,
            [
                "12:00-13:00",
                "13:00-14:00",
                "14:00-15:00",
                "15:00-16:00",
                "16:00-17:00",
                "17:00-18:00",
                "18:00-19:00",
                "19:00-20:00",
                "20:00-21:00",
                "21:00-22:00",
            ],
        )

    def test_crear_reserva_rechaza_bloque_sin_antelacion(self):
        with self.assertRaises(ValidationError):
            services.crear_reserva(
                self.usuario, self.sala, self.fecha, "10:00-11:00"
            )

    def test_crear_reserva_acepta_bloque_futuro(self):
        reserva = services.crear_reserva(
            self.usuario, self.sala, self.fecha, "15:00-16:00"
        )
        self.assertEqual(reserva.estado, Reserva.Estado.RESERVADA)

    def test_crear_reserva_rechaza_fuera_de_horizonte(self):
        with self.assertRaises(ValidationError):
            services.crear_reserva(
                self.usuario,
                self.sala,
                self.fecha + timedelta(days=services.MAX_DIAS_RESERVA + 1),
                "10:00-11:00",
            )

    def test_busqueda_form_rechaza_bloque_no_disponible(self):
        form = BusquedaForm(
            {
                "tipo": Recurso.Tipo.SALA,
                "fecha": self.fecha,
                "bloque": "10:00-11:00",
            }
        )
        self.assertFalse(form.is_valid())

    def test_reserva_form_rechaza_bloque_no_disponible(self):
        form = ReservaForm({"fecha": self.fecha, "bloque": "10:00-11:00"})
        self.assertFalse(form.is_valid())

    def test_endpoint_bloques_devuelve_solo_disponibles(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.get(
            "/buscar/bloques/", {"fecha": self.fecha.isoformat()}
        )
        self.assertEqual(respuesta.status_code, 200)
        valores = [b["valor"] for b in respuesta.json()["bloques"]]
        self.assertEqual(valores[0], "12:00-13:00")
        self.assertEqual(valores[-1], "21:00-22:00")
        self.assertEqual(len(valores), 10)


@override_settings(DEMO_MODE=True, DEMO_NOW="2026-11-12T09:00:00")
class CancelacionTests(TestCase):
    """Cancelación de reservas por el solicitante y el bibliotecario (RF-02)."""

    def setUp(self):
        self.hoy = services.hoy()
        self.estudiante = Usuario.objects.create_user(
            username="cancela@virginiogomez.cl",
            email="cancela@virginiogomez.cl",
            password="demo1234",
            rol=Usuario.Rol.SOLICITANTE,
        )
        self.otro = Usuario.objects.create_user(
            username="otro@virginiogomez.cl",
            email="otro@virginiogomez.cl",
            password="demo1234",
            rol=Usuario.Rol.SOLICITANTE,
        )
        self.bibliotecario = Usuario.objects.create_user(
            username="bib@virginiogomez.cl",
            email="bib@virginiogomez.cl",
            password="demo1234",
            rol=Usuario.Rol.BIBLIOTECARIO,
        )
        self.sala = Recurso.objects.create(
            nombre="Sala Cancelable", tipo=Recurso.Tipo.SALA
        )

    def _reserva(self, usuario=None, bloque="10:00-11:00"):
        return services.crear_reserva(
            usuario or self.estudiante, self.sala, self.hoy, bloque
        )

    def test_estudiante_cancela_y_libera_cupo(self):
        reserva = self._reserva()
        self.assertEqual(services.cupo_diario(self.estudiante, self.hoy)["usadas"], 1)
        self.client.force_login(self.estudiante)
        respuesta = self.client.post(f"/mis-reservas/{reserva.pk}/cancelar/")
        self.assertRedirects(respuesta, "/mis-reservas/")
        reserva.refresh_from_db()
        self.assertEqual(reserva.estado, Reserva.Estado.CANCELADA)
        self.assertEqual(reserva.cancelada_por, self.estudiante)
        self.assertEqual(
            reserva.motivo_cancelacion, Reserva.MotivoCancelacion.SOLICITUD
        )
        self.assertIsNotNone(reserva.cancelada_en)
        self.assertEqual(services.cupo_diario(self.estudiante, self.hoy)["usadas"], 0)

    def test_mis_reservas_muestra_el_cupo_real(self):
        self._reserva()
        self.client.force_login(self.estudiante)
        respuesta = self.client.get("/mis-reservas/")
        self.assertContains(respuesta, "1/2")
        self.assertContains(respuesta, "1 reserva disponible")

    def test_cancelar_se_oculta_si_el_bloque_empezo(self):
        reserva = Reserva.objects.create(
            usuario=self.estudiante,
            recurso=self.sala,
            fecha=self.hoy,
            bloque="09:00-10:00",  # ahora son las 09:00: ya comenzó
        )
        self.client.force_login(self.estudiante)
        respuesta = self.client.get("/mis-reservas/")
        self.assertNotContains(respuesta, f"/mis-reservas/{reserva.pk}/cancelar/")
        self.assertContains(respuesta, "El bloque ya comenzó.")

    def test_prestamo_muestra_el_vencimiento_relativo(self):
        libro = Recurso.objects.create(
            nombre="Libro Vence", tipo=Recurso.Tipo.LIBRO
        )
        Reserva.objects.create(
            usuario=self.estudiante,
            recurso=libro,
            fecha=self.hoy,
            modalidad=Reserva.Modalidad.PRESTAMO,
            fecha_vencimiento=self.hoy + timedelta(days=2),
        )
        self.client.force_login(self.estudiante)
        respuesta = self.client.get("/mis-reservas/")
        self.assertContains(respuesta, "vence en 2 días")

    def test_bloque_cancelado_queda_disponible(self):
        reserva = self._reserva()
        self.client.force_login(self.estudiante)
        self.client.post(f"/mis-reservas/{reserva.pk}/cancelar/")
        fila = next(
            f
            for f in services.estado_recursos(self.hoy, "10:00-11:00")
            if f["recurso"] == self.sala
        )
        self.assertTrue(fila["disponible"])

    def test_qr_de_reserva_cancelada_se_rechaza(self):
        reserva = self._reserva()
        codigo = reserva.qr.codigo
        self.client.force_login(self.estudiante)
        self.client.post(f"/mis-reservas/{reserva.pk}/cancelar/")
        with self.assertRaises(ValidationError) as error:
            services.validar_inicio(codigo)
        self.assertIn("cancelada", error.exception.messages[0].lower())

    def test_no_puede_cancelar_una_reserva_ajena(self):
        reserva = self._reserva(usuario=self.otro)
        self.client.force_login(self.estudiante)
        respuesta = self.client.post(f"/mis-reservas/{reserva.pk}/cancelar/")
        self.assertEqual(respuesta.status_code, 404)
        reserva.refresh_from_db()
        self.assertEqual(reserva.estado, Reserva.Estado.RESERVADA)

    def test_no_puede_cancelar_despues_de_empezar_el_bloque(self):
        reserva = self._reserva()
        despues = timezone.make_aware(datetime.combine(self.hoy, time(10, 30)))
        with self.assertRaises(ValidationError):
            services.cancelar_reserva(reserva, self.estudiante, momento=despues)
        reserva.refresh_from_db()
        self.assertEqual(reserva.estado, Reserva.Estado.RESERVADA)

    def test_bibliotecario_cancela_no_show_con_motivo(self):
        reserva = self._reserva()
        despues = timezone.make_aware(datetime.combine(self.hoy, time(10, 30)))
        cancelada = services.cancelar_reserva(
            reserva,
            self.bibliotecario,
            Reserva.MotivoCancelacion.NO_SHOW,
            momento=despues,
        )
        self.assertEqual(cancelada.estado, Reserva.Estado.CANCELADA)
        self.assertEqual(cancelada.cancelada_por, self.bibliotecario)
        self.assertEqual(
            cancelada.motivo_cancelacion, Reserva.MotivoCancelacion.NO_SHOW
        )

    def test_bibliotecario_necesita_motivo(self):
        reserva = self._reserva()
        with self.assertRaises(ValidationError):
            services.cancelar_reserva(reserva, self.bibliotecario, "")
        reserva.refresh_from_db()
        self.assertEqual(reserva.estado, Reserva.Estado.RESERVADA)

    def test_no_se_cancela_una_reserva_en_uso(self):
        reserva = self._reserva()
        reserva.estado = Reserva.Estado.EN_USO
        reserva.save(update_fields=["estado"])
        with self.assertRaises(ValidationError):
            services.cancelar_reserva(
                reserva, self.bibliotecario, Reserva.MotivoCancelacion.SOLICITUD
            )

    def test_estudiante_no_cancela_una_finalizada(self):
        reserva = self._reserva()
        reserva.estado = Reserva.Estado.FINALIZADA
        reserva.save(update_fields=["estado"])
        with self.assertRaises(ValidationError):
            services.cancelar_reserva(reserva, self.estudiante)

    def test_vista_del_panel_cancela_con_motivo(self):
        reserva = self._reserva()
        self.client.force_login(self.bibliotecario)
        respuesta = self.client.post(
            "/bibliotecario/cancelar/",
            {
                "reserva_id": reserva.pk,
                "motivo": Reserva.MotivoCancelacion.SOLICITUD,
            },
        )
        self.assertRedirects(respuesta, "/bibliotecario/")
        reserva.refresh_from_db()
        self.assertEqual(reserva.estado, Reserva.Estado.CANCELADA)

    def test_panel_rechaza_cancelacion_sin_motivo(self):
        reserva = self._reserva()
        self.client.force_login(self.bibliotecario)
        self.client.post("/bibliotecario/cancelar/", {"reserva_id": reserva.pk})
        reserva.refresh_from_db()
        self.assertEqual(reserva.estado, Reserva.Estado.RESERVADA)

    def test_la_cancelacion_del_panel_conserva_la_pestana(self):
        reserva = self._reserva()
        self.client.force_login(self.bibliotecario)
        respuesta = self.client.post(
            "/bibliotecario/cancelar/",
            {
                "reserva_id": reserva.pk,
                "motivo": Reserva.MotivoCancelacion.SOLICITUD,
                "tab": "reservas",
            },
        )
        self.assertRedirects(respuesta, "/bibliotecario/?tab=reservas")

    def test_estudiante_no_accede_al_panel(self):
        reserva = self._reserva()
        self.client.force_login(self.estudiante)
        respuesta = self.client.post(
            "/bibliotecario/cancelar/",
            {
                "reserva_id": reserva.pk,
                "motivo": Reserva.MotivoCancelacion.SOLICITUD,
            },
        )
        self.assertEqual(respuesta.status_code, 403)
