"""Pruebas automáticas de las reglas principales (RF-01, RF-03, RF-06, RF-07)."""
from datetime import date, datetime, time, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.utils import timezone

from . import services
from .forms import BusquedaForm, ReservaForm
from .models import Libro, QR, Recurso, Reserva, Sancion, Usuario


@override_settings(DEMO_MODE=True, DEMO_NOW="2026-11-12T09:00:00")
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
        self.fecha = date(2026, 11, 12)

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
            username="ventana@example.com",
            email="ventana@example.com",
            password="demo1234",
            rol=Usuario.Rol.SOLICITANTE,
        )
        self.sala = Recurso.objects.create(
            nombre="Sala 9", tipo=Recurso.Tipo.SALA
        )
        self.fecha = services.hoy()

    def test_bloques_disponibles_filtra_iniciados_y_sin_antelacion(self):
        valores = [valor for valor, _ in services.bloques_disponibles(self.fecha)]
        self.assertEqual(valores, ["15:00-16:00"])

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
        self.assertEqual(valores, ["15:00-16:00"])


@override_settings(DEMO_MODE=True, DEMO_NOW="2026-11-12T09:00:00")
class InventarioTests(TestCase):
    """Estado agregado del inventario para el panel del bibliotecario."""

    def setUp(self):
        self.hoy = services.hoy()
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
        respuesta = self.client.get("/bibliotecario/")
        self.assertContains(respuesta, "En préstamo")
        self.assertContains(respuesta, "Préstamo hasta")

    def test_bibliotecario_no_ve_el_catalogo(self):
        self.client.force_login(self.bibliotecario)
        respuesta = self.client.get("/libros/", follow=True)
        self.assertContains(respuesta, "Panel de gestión")
        self.assertEqual(respuesta.redirect_chain[-1][0], "/bibliotecario/")


@override_settings(DEMO_MODE=True, DEMO_NOW="2026-11-12T09:00:00")
class InterfazTests(TestCase):
    """Comprobaciones de las vistas que sostienen la interfaz (RNF-02)."""

    def setUp(self):
        self.hoy = services.hoy()
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
        ayer = services.hoy() - timedelta(days=1)
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
        ayer = services.hoy() - timedelta(days=1)
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
            respuesta, f'min="{services.hoy().isoformat()}"'
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
