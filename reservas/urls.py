"""Rutas de la aplicación reservas."""
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="reservas/login.html", redirect_authenticated_user=True
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("buscar/", views.buscar, name="buscar"),
    path("reservar/<int:recurso_id>/", views.confirmar, name="confirmar"),
    path("reserva/<int:reserva_id>/qr/", views.qr_view, name="qr"),
    path("bibliotecario/", views.bibliotecario, name="bibliotecario"),
    path("bibliotecario/validar/", views.validar, name="validar"),
    path("bibliotecario/devolver/", views.devolver, name="devolver"),
]
