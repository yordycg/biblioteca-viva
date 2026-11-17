"""Registro de modelos en el admin (apoyo a la demo y al seed)."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import QR, Recurso, Reserva, Sancion, Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("BibliotecaViva", {"fields": ("rol", "sancionado_hasta")}),
    )
    list_display = ("username", "email", "rol", "sancionado_hasta", "is_staff")
    list_filter = ("rol", "is_staff")


@admin.register(Recurso)
class RecursoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "ubicacion", "capacidad", "estado")
    list_filter = ("tipo", "estado")
    search_fields = ("nombre", "codigo")


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "usuario", "recurso", "fecha", "bloque", "estado")
    list_filter = ("estado", "fecha", "bloque")
    search_fields = ("usuario__username", "recurso__nombre")


@admin.register(QR)
class QRAdmin(admin.ModelAdmin):
    list_display = ("codigo", "reserva", "utilizado", "generado_en")
    list_filter = ("utilizado",)


@admin.register(Sancion)
class SancionAdmin(admin.ModelAdmin):
    list_display = ("usuario", "inicio", "fin", "motivo")
    search_fields = ("usuario__username",)
