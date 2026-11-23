"""Interfaz de búsqueda, reserva y panel (RF-01, RF-02, RF-08)."""
from datetime import date, datetime, time, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.utils import timezone

from reservas import services
from reservas.forms import BusquedaForm, ReservaForm
from reservas.models import Libro, QR, Recurso, Reserva, Sancion, Usuario

@override_settings(DEMO_MODE=True, DEMO_NOW="2026-11-12T09:00:00")
class InterfazTests(TestCase):
    """Comprobaciones de las vistas que sostienen la interfaz (RNF-02)."""

    def setUp(self):
        self.hoy = services.hoy()
        self.estudiante = Usuario.objects.create_user(
            username="e@virginiogomez.cl",
            email="e@virginiogomez.cl",
            password="demo1234",
            rol=Usuario.Rol.SOLICITANTE,
        )
        self.bibliotecario = Usuario.objects.create_user(
            username="b@virginiogomez.cl",
            email="b@virginiogomez.cl",
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
                "vista": "recursos",
                "filtrar": "1",
                "tipo": Recurso.Tipo.SALA,
                "fecha": ayer.isoformat(),
                "bloque": "10:00-11:00",
            },
        )
        self.assertContains(respuesta, "no puede ser anterior a hoy")
        self.assertEqual(respuesta.context["recursos"], [])

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

    def test_busqueda_ofrece_bloques_sin_javascript(self):
        """El selector de bloque trae el catálogo aunque no haya fecha (DEF-03).

        Con JavaScript el listado se reemplaza por los bloques disponibles de la
        fecha elegida; sin JavaScript el formulario igual debe poder enviarse.
        """
        self.client.force_login(self.estudiante)
        respuesta = self.client.get("/buscar/")
        opciones = list(respuesta.context["form"].fields["bloque"].choices)
        self.assertEqual(len(opciones), len(Reserva.BLOQUES) + 1)
        self.assertIn("10:00-11:00", [valor for valor, _ in opciones])

    def test_panel_bibliotecario_lista_reservas_del_dia(self):
        self.client.force_login(self.bibliotecario)
        respuesta = self.client.get("/bibliotecario/", {"tab": "reservas"})
        self.assertContains(respuesta, self.reserva.codigo)
        self.assertContains(respuesta, "Reservas del día")
        self.assertContains(respuesta, "Sala 3")

    def test_panel_muestra_estado_del_inventario(self):
        self.client.force_login(self.bibliotecario)
        respuesta = self.client.get("/bibliotecario/", {"tab": "inventario"})
        self.assertContains(respuesta, "Estado del inventario")
        self.assertContains(respuesta, "Disponibles hoy")
        self.assertContains(respuesta, "Ocupación del día")
        self.assertContains(respuesta, "Sala 3")

    def test_panel_muestra_las_cuatro_pestanas(self):
        self.client.force_login(self.bibliotecario)
        respuesta = self.client.get("/bibliotecario/")
        for clave in ("operacion", "inventario", "reservas", "validacion"):
            self.assertContains(respuesta, f"tab={clave}")
        self.assertContains(respuesta, 'aria-current="page">Operación')

    def test_cada_pestana_renderiza_su_seccion(self):
        self.client.force_login(self.bibliotecario)
        operacion = self.client.get("/bibliotecario/").content.decode()
        self.assertIn('id="entregas-title"', operacion)
        self.assertNotIn('id="inventario"', operacion)
        inventario = self.client.get(
            "/bibliotecario/", {"tab": "inventario"}
        ).content.decode()
        self.assertIn('id="inventario"', inventario)
        self.assertNotIn('id="dia-title"', inventario)
        reservas = self.client.get(
            "/bibliotecario/", {"tab": "reservas"}
        ).content.decode()
        self.assertIn('id="dia-title"', reservas)
        self.assertNotIn('id="inventario"', reservas)
        validacion = self.client.get(
            "/bibliotecario/", {"tab": "validacion"}
        ).content.decode()
        self.assertIn('id="validacion-title"', validacion)
        self.assertNotIn('id="dia-title"', validacion)

    def test_un_codigo_abre_la_pestana_de_validacion(self):
        self.client.force_login(self.bibliotecario)
        respuesta = self.client.get(
            "/bibliotecario/", {"codigo": self.reserva.codigo}
        )
        self.assertIn(
            'id="validacion-title"', respuesta.content.decode()
        )

    def test_panel_muestra_resumen_operativo(self):
        self.client.force_login(self.bibliotecario)
        respuesta = self.client.get("/bibliotecario/")
        self.assertContains(respuesta, "Reservas hoy")
        self.assertContains(respuesta, "Pendientes de entrega")
        self.assertContains(respuesta, "Próximas entregas")
        self.assertContains(respuesta, "Devoluciones de libros")
        self.assertContains(respuesta, "Ocupación por bloque")
        self.assertContains(respuesta, "Sanciones activas")

    def test_panel_filtra_tabla_por_estado(self):
        self.client.force_login(self.bibliotecario)
        visible = self.client.get(
            "/bibliotecario/", {"estado": "RESERVADA"}
        )
        self.assertContains(visible, "1 de 1")
        oculto = self.client.get(
            "/bibliotecario/", {"estado": "FINALIZADA"}
        )
        self.assertContains(oculto, "0 de 1")
        self.assertContains(oculto, "No hay reservas que coincidan")

    def test_panel_busca_por_codigo(self):
        self.client.force_login(self.bibliotecario)
        respuesta = self.client.get(
            "/bibliotecario/", {"q": self.reserva.codigo}
        )
        self.assertContains(respuesta, "1 de 1")

    def test_barra_superior_no_muestra_rol(self):
        self.client.force_login(self.estudiante)
        respuesta = self.client.get("/buscar/")
        self.assertNotContains(respuesta, "Solicitante")

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

    def test_login_vacio_muestra_errores_por_campo(self):
        respuesta = self.client.post(
            "/login/", {"username": "", "password": ""}
        )
        self.assertContains(respuesta, "Ingresa tu correo institucional.")
        self.assertContains(respuesta, "Ingresa tu contraseña.")
        self.assertContains(respuesta, "field--error")

    def test_login_no_expone_credenciales_de_demo(self):
        respuesta = self.client.get("/login/")
        self.assertNotContains(respuesta, "Credenciales de prueba")
        self.assertNotContains(respuesta, "estudiante1@virginiogomez.cl")
        self.assertNotContains(respuesta, "demo1234")

    def test_barra_superior_muestra_logo_institucional(self):
        self.client.force_login(self.estudiante)
        respuesta = self.client.get("/buscar/")
        self.assertContains(respuesta, "reservas/img/ipvg-logo.png")
        self.assertContains(respuesta, "BibliotecaViva")

    def test_login_valido_redirige(self):
        respuesta = self.client.post(
            "/login/", {"username": "e@virginiogomez.cl", "password": "demo1234"}
        )
        self.assertRedirects(respuesta, "/", fetch_redirect_response=False)

    def test_login_invalido_muestra_error(self):
        respuesta = self.client.post(
            "/login/", {"username": "e@virginiogomez.cl", "password": "incorrecta"}
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Correo o contraseña incorrectos")

    def test_busqueda_muestra_aviso_de_sancion(self):
        self.estudiante.sancionado_hasta = timezone.now() + timedelta(days=7)
        self.estudiante.save(update_fields=["sancionado_hasta"])
        self.client.force_login(self.estudiante)
        respuesta = self.client.get("/buscar/")
        self.assertContains(respuesta, "Sanción vigente")
