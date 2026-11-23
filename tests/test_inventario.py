"""Inventario del panel, catálogo inicial y bloques del día (RF-01)."""
from datetime import date, datetime, time, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.utils import timezone

from reservas import services
from reservas.forms import BusquedaForm, ReservaForm
from reservas.models import Libro, QR, Recurso, Reserva, Sancion, Usuario

@override_settings(DEMO_MODE=True, DEMO_NOW="2026-11-12T09:00:00")
class InventarioTests(TestCase):
    """Estado agregado del inventario para el panel del bibliotecario."""

    def setUp(self):
        self.hoy = services.hoy()
        self.usuario = Usuario.objects.create_user(
            username="inv@virginiogomez.cl",
            email="inv@virginiogomez.cl",
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

    def test_sin_filtros_devuelve_todas_las_filas(self):
        inventario = services.estado_inventario(self.hoy)
        self.assertEqual(inventario["filtradas"], 4)
        self.assertEqual(inventario["total_filas"], 4)
        self.assertFalse(inventario["filtrado"])

    def test_filtro_por_texto_acota_las_filas(self):
        inventario = services.estado_inventario(self.hoy, "proyector")
        self.assertEqual(inventario["filtradas"], 1)
        self.assertEqual(
            inventario["filas"][0]["recurso"], self.equipo_en_uso
        )
        # Los contadores siguen siendo globales
        self.assertEqual(inventario["resumen"]["total"], 4)
        self.assertTrue(inventario["filtrado"])

    def test_filtro_por_tipo_y_estado(self):
        por_tipo = services.estado_inventario(
            self.hoy, "", Recurso.Tipo.SALA, ""
        )
        self.assertEqual(por_tipo["filtradas"], 2)
        por_estado = services.estado_inventario(self.hoy, "", "", "RESERVADO")
        self.assertEqual(por_estado["filtradas"], 1)
        self.assertEqual(
            por_estado["filas"][0]["recurso"], self.sala_reservada
        )

    def test_panel_filtra_el_inventario_sin_alterar_los_contadores(self):
        bibliotecario = Usuario.objects.create_user(
            username="inv-panel@virginiogomez.cl",
            email="inv-panel@virginiogomez.cl",
            password="demo1234",
            rol=Usuario.Rol.BIBLIOTECARIO,
        )
        self.client.force_login(bibliotecario)
        respuesta = self.client.get("/bibliotecario/", {"inv_q": "Proyector"})
        self.assertContains(respuesta, "Mostrando <strong>1</strong> de")
        self.assertContains(respuesta, "Recursos")


@override_settings(DEMO_MODE=True, DEMO_NOW="2026-11-12T09:00:00")
class CatalogoInicialTests(TestCase):
    """Catálogo inicial con estado y filtros explícitos."""

    def setUp(self):
        self.hoy = services.hoy()
        self.usuario = Usuario.objects.create_user(
            username="catalogo@virginiogomez.cl",
            email="catalogo@virginiogomez.cl",
            password="demo1234",
            rol=Usuario.Rol.SOLICITANTE,
        )
        self.bibliotecario = Usuario.objects.create_user(
            username="panel@virginiogomez.cl",
            email="panel@virginiogomez.cl",
            password="demo1234",
            rol=Usuario.Rol.BIBLIOTECARIO,
        )
        self.sala = Recurso.objects.create(
            nombre="Sala Catálogo", tipo=Recurso.Tipo.SALA, capacidad=6
        )
        self.equipo = Recurso.objects.create(
            nombre="Proyector Catálogo", tipo=Recurso.Tipo.EQUIPO
        )
        self.libro = Libro.objects.create(
            nombre="Libro Catálogo",
            autor="Autora de Prueba",
            genero="Novela",
            portada="reservas/covers/quijote.svg",
        )

    def test_hay_trece_bloques_de_09_a_22(self):
        self.assertEqual(len(Reserva.BLOQUES), 13)
        self.assertEqual(Reserva.BLOQUES[0][0], "09:00-10:00")
        self.assertEqual(Reserva.BLOQUES[-1][0], "21:00-22:00")

    def test_libros_inicial_muestra_el_catalogo(self):
        """El catálogo de libros aparece completo al entrar, sin filtrar."""
        self.client.force_login(self.usuario)
        respuesta = self.client.get("/buscar/", {"vista": "libros"})
        self.assertContains(respuesta, "Libro Catálogo")
        self.assertNotContains(respuesta, "Elige una fecha de retiro")
        self.assertIsNone(respuesta.context["form_libros"]["dias"].value())
        self.assertTrue(respuesta.context["tarjetas"])
        self.assertNotContains(respuesta, "field--error")

    def test_recursos_inicial_muestra_el_catalogo(self):
        """Salas y equipos se listan desde el inicio con el próximo bloque."""
        self.client.force_login(self.usuario)
        respuesta = self.client.get("/buscar/", {"vista": "recursos"})
        self.assertContains(respuesta, "Sala Catálogo")
        self.assertContains(respuesta, "Proyector Catálogo")
        self.assertNotContains(respuesta, "Elige una fecha y un bloque horario")
        self.assertNotContains(respuesta, "field--error")

    def test_formulario_vacio_sin_filtros(self):
        """Los filtros se pintan vacíos; el listado usa el próximo bloque."""
        self.client.force_login(self.usuario)
        respuesta = self.client.get("/buscar/", {"vista": "recursos"})
        self.assertIsNone(respuesta.context["form"]["fecha"].value())
        self.assertIsNone(respuesta.context["form"]["bloque"].value())
        self.assertEqual(respuesta.context["bloque"], "10:00-11:00")
        self.assertTrue(respuesta.context["recursos"])

    def test_filtros_solo_validan_con_filtrar(self):
        self.client.force_login(self.usuario)
        sin_enviar = self.client.get(
            "/buscar/", {"vista": "libros", "fecha": "", "dias": ""}
        )
        self.assertNotContains(sin_enviar, "field--error")
        enviado = self.client.get(
            "/buscar/",
            {"vista": "libros", "filtrar": "1", "fecha": "", "dias": ""},
        )
        self.assertContains(enviado, "field--error")

    def test_recurso_ocupado_visible_con_estado(self):
        Reserva.objects.create(
            usuario=self.usuario,
            recurso=self.sala,
            fecha=self.hoy,
            bloque="10:00-11:00",
        )
        self.client.force_login(self.usuario)
        respuesta = self.client.get(
            "/buscar/",
            {
                "vista": "recursos",
                "filtrar": "1",
                "fecha": self.hoy.isoformat(),
                "bloque": "10:00-11:00",
            },
        )
        self.assertContains(respuesta, "Sala Catálogo")
        self.assertContains(respuesta, "Reservado")

    def test_solo_disponibles_oculta_ocupados(self):
        Reserva.objects.create(
            usuario=self.usuario,
            recurso=self.sala,
            fecha=self.hoy,
            bloque="10:00-11:00",
        )
        self.client.force_login(self.usuario)
        respuesta = self.client.get(
            "/buscar/",
            {
                "vista": "recursos",
                "filtrar": "1",
                "tipo": "",
                "fecha": self.hoy.isoformat(),
                "bloque": "10:00-11:00",
                "solo_disponibles": "on",
            },
        )
        self.assertNotContains(respuesta, "Sala Catálogo")
        self.assertContains(respuesta, "Proyector Catálogo")

    def test_panel_muestra_timeline_de_bloques(self):
        self.client.force_login(self.bibliotecario)
        respuesta = self.client.get("/bibliotecario/", {"tab": "inventario"})
        html = respuesta.content.decode()
        self.assertContains(respuesta, "timeline__track")
        self.assertEqual(html.count('class="timeline__slot'), 26)


@override_settings(DEMO_MODE=True, DEMO_NOW="2026-11-12T21:50:00")
class SinBloquesHoyTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="sinbloques@virginiogomez.cl",
            email="sinbloques@virginiogomez.cl",
            password="demo1234",
            rol=Usuario.Rol.SOLICITANTE,
        )

    def test_avisa_cuando_la_fecha_no_tiene_bloques(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.get(
            "/buscar/",
            {
                "vista": "recursos",
                "filtrar": "1",
                "fecha": services.hoy().isoformat(),
                "bloque": "21:00-22:00",
            },
        )
        self.assertRegex(
            respuesta.content.decode(),
            r'id="aviso-sin-bloques"\s+role="alert">',
        )

    def test_no_avisa_cuando_hay_bloques(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.get(
            "/buscar/",
            {
                "vista": "recursos",
                "filtrar": "1",
                "fecha": (services.hoy() + timedelta(days=1)).isoformat(),
                "bloque": "10:00-11:00",
            },
        )
        self.assertRegex(
            respuesta.content.decode(),
            r'id="aviso-sin-bloques"\s+role="alert"\s+style="display: none;"',
        )
