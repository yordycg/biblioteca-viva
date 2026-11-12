"""Formularios de BibliotecaViva (RF-01, RF-02, RF-04, RF-05)."""
from datetime import date, timedelta

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
        hoy = services.hoy()
        if fecha < hoy:
            raise forms.ValidationError(
                "La fecha no puede ser anterior a hoy. Elige hoy o un día posterior."
            )
        if fecha > hoy + timedelta(days=services.MAX_DIAS_RESERVA):
            raise forms.ValidationError(
                "La fecha no puede superar los próximos "
                f"{services.MAX_DIAS_RESERVA} días."
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fecha = None
        if self.is_bound:
            fecha = self.data.get(self.add_prefix("fecha"))
        if not fecha:
            fecha = self.initial.get("fecha")
        if fecha:
            if isinstance(fecha, str):
                try:
                    fecha = date.fromisoformat(fecha)
                except ValueError:
                    fecha = None
            if fecha:
                self.fields["bloque"].choices = services.bloques_disponibles(fecha)

    def clean(self):
        data = super().clean()
        fecha = data.get("fecha")
        bloque = data.get("bloque")
        if fecha and bloque and services.fecha_reservable(fecha):
            disponibles = dict(services.bloques_disponibles(fecha))
            if bloque not in disponibles:
                raise forms.ValidationError(
                    "El bloque seleccionado ya no está disponible para esa fecha. "
                    "Elige otro bloque."
                )
        return data


class ReservaForm(FechaDesdeHoyMixin, forms.Form):
    fecha = forms.DateField(widget=forms.HiddenInput)
    bloque = forms.ChoiceField(choices=Reserva.BLOQUES, widget=forms.HiddenInput)

    def clean(self):
        data = super().clean()
        fecha = data.get("fecha")
        bloque = data.get("bloque")
        if fecha and bloque:
            if bloque not in dict(Reserva.BLOQUES):
                raise forms.ValidationError("El bloque horario no es válido.")
            if not services.bloque_vigente(bloque, fecha):
                raise forms.ValidationError(
                    "El bloque ya comenzó o no cumple la antelación mínima de "
                    f"{services.MIN_ANTELACION_MIN} minutos. Elige otro bloque."
                )
        return data


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
