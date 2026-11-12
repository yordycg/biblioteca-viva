"""Rutas de la aplicación reservas."""
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import LoginForm

urlpatterns = [
    path("", views.home, name="home"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="reservas/login.html",
            authentication_form=LoginForm,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("buscar/", views.buscar, name="buscar"),
    path("buscar/bloques/", views.bloques, name="bloques_disponibles"),
    path("libros/", views.catalogo, name="catalogo"),
    path("libros/<int:libro_id>/", views.libro_detalle, name="libro"),
    path("mis-reservas/", views.mis_reservas, name="mis_reservas"),
    path("reservar/<int:recurso_id>/", views.confirmar, name="confirmar"),
    path("reserva/<int:reserva_id>/qr/", views.qr_view, name="qr"),
    path("bibliotecario/", views.bibliotecario, name="bibliotecario"),
    path("bibliotecario/validar/", views.validar, name="validar"),
    path("bibliotecario/devolver/", views.devolver, name="devolver"),
]
