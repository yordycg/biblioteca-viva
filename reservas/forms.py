"""Formularios de BibliotecaViva (RF-01, RF-02, RF-04, RF-05)."""
from django import forms

from . import services
from .models import Reserva, Recurso


class FechaDesdeHoyMixin:
    """Impide elegir fechas anteriores al día actual (RF-01, RF-02)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        campo = self.fields.get("fecha")
        if campo:
            campo.widget.attrs["min"] = services.hoy().isoformat()

    def clean_fecha(self):
        fecha = self.cleaned_data["fecha"]
        if fecha < services.hoy():
            raise forms.ValidationError(
                "La fecha no puede ser anterior a hoy. Elige hoy o un día posterior."
            )
        return fecha


class BusquedaForm(FechaDesdeHoyMixin, forms.Form):
    tipo = forms.ChoiceField(
        label="Tipo de recurso",
        choices=Recurso.Tipo.choices,
        widget=forms.Select(attrs={"class": "campo"}),
    )
    fecha = forms.DateField(
        label="Fecha",
        widget=forms.DateInput(attrs={"class": "campo", "type": "date"}),
    )
    bloque = forms.ChoiceField(
        label="Bloque horario",
        choices=Reserva.BLOQUES,
        widget=forms.Select(attrs={"class": "campo"}),
    )


class ReservaForm(FechaDesdeHoyMixin, forms.Form):
    fecha = forms.DateField(widget=forms.HiddenInput)
    bloque = forms.ChoiceField(choices=Reserva.BLOQUES, widget=forms.HiddenInput)


class CodigoQRForm(forms.Form):
    codigo = forms.CharField(
        label="Código del QR",
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "campo",
                "placeholder": "Ej.: RSV-0001",
                "autocomplete": "off",
            }
        ),
    )
