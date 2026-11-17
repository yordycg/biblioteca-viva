"""Préstamo de libros y catálogo bibliográfico (RF-01, RF-02, RF-06)."""
from datetime import date, datetime, time, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.utils import timezone

from reservas import services
from reservas.forms import BusquedaForm, ReservaForm
from reservas.models import Libro, QR, Recurso, Reserva, Sancion, Usuario

@override_settings(DEMO_MODE=True, DEMO_NOW="2026-11-12T09:00:00")
class LibroTests(TestCase):
    """Catálogo y reserva de libros (RF-01, RF-02)."""

    def setUp(self):
        self.hoy = services.hoy()
        self.usuario = Usuario.objects.create_user(
            username="libro@example.com",
            email="libro@example.com",
            password="demo1234",
            rol=Usuario.Rol.SOLICITANTE,
        )
        self.bibliotecario = Usuario.objects.create_user(
            username="biblioteca@example.com",
            email="biblioteca@example.com",
            password="demo1234",
            rol=Usuario.Rol.BIBLIOTECARIO,
        )
        self.libro = Libro.objects.create(
            nombre="Don Quijote de la Mancha",
            autor="Miguel de Cervantes",
            editorial="Ediciones BibliotecaViva",
            anio=1605,
            isbn="978-956-00-0001-1",
            genero="Novela",
            paginas=863,
            ubicacion="Estante A-1",
            codigo="lib-001",
            portada="reservas/covers/quijote.svg",
            sinopsis="Aventuras de Alonso Quijano.",
        )
        self.libro2 = Libro.objects.create(
            nombre="Martín Fierro",
            autor="José Hernández",
            genero="Poesía",
            portada="reservas/covers/martin-fierro.svg",
        )

    def test_libro_se_crea_con_tipo_libro(self):
        self.assertEqual(self.libro.tipo, Recurso.Tipo.LIBRO)
        self.assertEqual(self.libro.get_tipo_display(), "Libro")

    def test_busqueda_de_recursos_no_ofrece_libros(self):
        form = BusquedaForm()
        self.assertNotIn(
            Recurso.Tipo.LIBRO, dict(form.fields["tipo"].choices)
        )

    def test_catalogo_filtra_por_autor(self):
        tarjetas = services.catalogo_libros(self.hoy, "Cervantes")
        self.assertEqual([t["libro"].id for t in tarjetas], [self.libro.id])

    def test_catalogo_filtra_por_genero(self):
        tarjetas = services.catalogo_libros(self.hoy, genero="Novela")
        self.assertEqual([t["libro"].id for t in tarjetas], [self.libro.id])
        self.assertEqual(
            services.catalogo_libros(self.hoy, genero="Terror"), []
        )

    def test_prestamo_genera_qr_y_vencimiento(self):
        reserva = services.crear_reserva(
            self.usuario, self.libro, self.hoy, dias=7
        )
        self.assertEqual(reserva.modalidad, Reserva.Modalidad.PRESTAMO)
        self.assertEqual(reserva.fecha_vencimiento, self.hoy + timedelta(days=7))
        self.assertTrue(QR.objects.filter(reserva=reserva).exists())

    def test_prestamo_rechaza_duracion_invalida(self):
        with self.assertRaises(ValidationError):
            services.crear_reserva(
                self.usuario, self.libro, self.hoy, dias=5
            )

    def test_prestamo_solapado_rechazado(self):
        services.crear_reserva(self.usuario, self.libro, self.hoy, dias=7)
        with self.assertRaises(ValidationError):
            services.crear_reserva(
                self.usuario,
                self.libro,
                self.hoy + timedelta(days=3),
                dias=7,
            )

    def test_limite_de_prestamos_activos(self):
        services.crear_reserva(self.usuario, self.libro, self.hoy, dias=7)
        services.crear_reserva(self.usuario, self.libro2, self.hoy, dias=7)
        otro = Libro.objects.create(
            nombre="La Araucana", autor="Alonso de Ercilla"
        )
        with self.assertRaises(ValidationError):
            services.crear_reserva(self.usuario, otro, self.hoy, dias=7)

    def test_catalogo_marca_libro_no_disponible(self):
        services.crear_reserva(self.usuario, self.libro, self.hoy, dias=7)
        tarjeta = next(
            t for t in services.catalogo_libros(self.hoy) if t["libro"] == self.libro
        )
        self.assertFalse(tarjeta["disponible"])
        self.assertIsNotNone(tarjeta["desde"])

    def test_inventario_incluye_libros(self):
        inventario = services.estado_inventario(self.hoy)
        tipos = {t["tipo"]: t for t in inventario["por_tipo"]}
        self.assertEqual(tipos[Recurso.Tipo.LIBRO]["total"], 2)

    def test_busqueda_libros_marca_campo_con_error(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.get(
            "/buscar/",
            {"vista": "libros", "filtrar": "1", "fecha": "", "dias": ""},
        )
        self.assertContains(respuesta, "field--error")
        self.assertContains(respuesta, "Elige una fecha de retiro.")
        self.assertContains(respuesta, "Elige una duración de 3, 7 o 14 días.")
        self.assertContains(respuesta, 'id="error-fecha"')
        self.assertContains(respuesta, 'aria-invalid="true"')
        self.assertNotContains(respuesta, "Este campo es obligatorio.")

    def test_busqueda_recursos_marca_campo_con_error(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.get(
            "/buscar/",
            {
                "vista": "recursos",
                "filtrar": "1",
                "tipo": "SALA",
                "fecha": "",
                "bloque": "",
            },
        )
        self.assertContains(respuesta, "field--error")
        self.assertContains(respuesta, "Elige una fecha.")
        self.assertContains(respuesta, "Elige un bloque horario.")
        self.assertContains(respuesta, 'id="error-fecha-recursos"')

    def test_ficha_libro_marca_campo_con_error(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.get(
            f"/libros/{self.libro.id}/", {"fecha": "", "dias": ""}
        )
        self.assertContains(respuesta, "field--error")
        self.assertContains(respuesta, "Elige una fecha de retiro.")
        self.assertContains(respuesta, 'id="error-fecha-prestamo"')

    def test_catalogo_lista_libros_con_portada(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.get(
            "/buscar/",
            {
                "vista": "libros",
                "fecha": self.hoy.isoformat(),
                "dias": 7,
            },
        )
        self.assertContains(respuesta, "Don Quijote de la Mancha")
        self.assertContains(respuesta, "Miguel de Cervantes")
        self.assertContains(respuesta, "reservas/covers/quijote.svg")

    def test_ficha_libro_muestra_metadatos_y_prestamo(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.get(f"/libros/{self.libro.id}/")
        self.assertContains(respuesta, "978-956-00-0001-1")
        self.assertContains(respuesta, "Miguel de Cervantes")
        self.assertContains(respuesta, "Solicitar préstamo")
        self.assertContains(respuesta, "Devolución estimada")

    def test_reservar_libro_genera_qr(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.post(
            f"/reservar/{self.libro.id}/",
            {"fecha": self.hoy.isoformat(), "dias": 7},
        )
        reserva = Reserva.objects.get(recurso=self.libro)
        self.assertRedirects(
            respuesta,
            f"/reserva/{reserva.pk}/qr/",
            fetch_redirect_response=False,
        )
        self.assertEqual(reserva.estado, Reserva.Estado.RESERVADA)
        self.assertTrue(QR.objects.filter(reserva=reserva).exists())

    def test_busqueda_tipo_libro_muestra_autor(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.get(
            "/buscar/",
            {
                "vista": "libros",
                "fecha": self.hoy.isoformat(),
                "dias": 7,
                "q": "Cervantes",
            },
        )
        self.assertContains(respuesta, "Don Quijote de la Mancha")
        self.assertContains(respuesta, "Miguel de Cervantes")
        self.assertContains(respuesta, "reservas/covers/quijote.svg")

    def test_ficha_continuar_redirige_a_confirmacion(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.get(
            f"/libros/{self.libro.id}/",
            {
                "fecha": self.hoy.isoformat(),
                "dias": 7,
                "continuar": 1,
            },
        )
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(
            f"/reservar/{self.libro.id}/?fecha={self.hoy.isoformat()}&dias=7",
            respuesta.url,
        )

    def test_confirmar_libro_muestra_resumen(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.get(
            f"/reservar/{self.libro.id}/",
            {"fecha": self.hoy.isoformat(), "dias": 7},
        )
        self.assertContains(respuesta, "Datos del préstamo")
        self.assertContains(respuesta, "Devolución")

    def test_devolucion_tardia_de_prestamo_aplica_sancion(self):
        reserva = services.crear_reserva(
            self.usuario, self.libro, self.hoy, dias=7
        )
        inicio = timezone.make_aware(
            datetime.combine(self.hoy, time(10, 5))
        )
        services.validar_inicio(reserva.codigo, inicio)
        tarde = timezone.make_aware(
            datetime.combine(
                self.hoy + timedelta(days=8), time(10, 0)
            )
        )
        reserva, sancion = services.registrar_devolucion(
            reserva.codigo, tarde
        )
        self.assertEqual(reserva.estado, Reserva.Estado.FINALIZADA)
        self.assertIsNotNone(sancion)
        self.usuario.refresh_from_db()
        self.assertIsNotNone(self.usuario.sancionado_hasta)

    def test_panel_muestra_prestamo_de_libro(self):
        services.crear_reserva(self.usuario, self.libro, self.hoy, dias=7)
        self.client.force_login(self.bibliotecario)
        respuesta = self.client.get("/bibliotecario/", {"tab": "reservas"})
        self.assertContains(respuesta, "Préstamo hasta")
        self.assertContains(respuesta, "Reservada")

    def test_bibliotecario_no_ve_el_catalogo(self):
        self.client.force_login(self.bibliotecario)
        respuesta = self.client.get("/libros/", follow=True)
        self.assertContains(respuesta, "Panel de gestión")
        self.assertEqual(respuesta.redirect_chain[-1][0], "/bibliotecario/")
