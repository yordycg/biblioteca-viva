"""Formularios de BibliotecaViva (RF-01, RF-02, RF-04, RF-05)."""
from datetime import date, timedelta

from django import forms
from django.contrib.auth.forms import AuthenticationForm

from . import services
from .models import Reserva, Recurso


class LoginForm(AuthenticationForm):
    """Login con mensajes de campo en español."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].error_messages["required"] = (
            "Ingresa tu correo institucional."
        )
        self.fields["password"].error_messages["required"] = (
            "Ingresa tu contraseña."
        )


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
        choices=[
            ("", "Todos"),
            (Recurso.Tipo.SALA, "Sala"),
            (Recurso.Tipo.EQUIPO, "Equipo"),
        ],
        required=False,
        error_messages={
            "required": "Elige un tipo de recurso.",
            "invalid_choice": "Elige un tipo de recurso válido.",
        },
        widget=forms.Select(attrs={"class": "campo"}),
    )
    fecha = forms.DateField(
        label="Fecha",
        error_messages={
            "required": "Elige una fecha.",
            "invalid": "Ingresa una fecha válida.",
        },
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={"class": "campo", "type": "date"},
        ),
    )
    bloque = forms.ChoiceField(
        label="Bloque horario",
        choices=Reserva.BLOQUES,
        error_messages={
            "required": "Elige un bloque horario.",
            "invalid_choice": "Elige un bloque horario válido.",
        },
        widget=forms.Select(attrs={"class": "campo"}),
    )
    solo_disponibles = forms.BooleanField(
        label="Solo disponibles",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "check"}),
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
                disponibles = services.bloques_disponibles(fecha)
                self.fields["bloque"].choices = [
                    ("", "Elige un bloque")
                ] + disponibles

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
    fecha = forms.DateField(widget=forms.HiddenInput())
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


class DiasPrestamoMixin:
    """Valida la duración del préstamo de un libro."""

    def clean_dias(self):
        dias = self.cleaned_data["dias"]
        if dias not in services.DIAS_PRESTAMO:
            raise forms.ValidationError(
                "La duración debe ser de 3, 7 o 14 días."
            )
        return dias


class PrestamoForm(FechaDesdeHoyMixin, DiasPrestamoMixin, forms.Form):
    fecha = forms.DateField(
        label="Fecha de retiro",
        error_messages={
            "required": "Elige una fecha de retiro.",
            "invalid": "Ingresa una fecha válida.",
        },
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={"class": "campo", "type": "date"},
        ),
    )
    dias = forms.TypedChoiceField(
        label="Duración",
        choices=[("", "Elige una duración")]
        + [(dias, f"{dias} días") for dias in services.DIAS_PRESTAMO],
        coerce=int,
        error_messages={
            "required": "Elige una duración de 3, 7 o 14 días.",
            "invalid_choice": "Elige una duración válida.",
        },
        widget=forms.Select(attrs={"class": "campo"}),
    )


class BusquedaLibrosForm(FechaDesdeHoyMixin, DiasPrestamoMixin, forms.Form):
    fecha = forms.DateField(
        label="Fecha de retiro",
        error_messages={
            "required": "Elige una fecha de retiro.",
            "invalid": "Ingresa una fecha válida.",
        },
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={"class": "campo", "type": "date"},
        ),
    )
    dias = forms.TypedChoiceField(
        label="Duración",
        choices=[("", "Elige una duración")]
        + [(dias, f"{dias} días") for dias in services.DIAS_PRESTAMO],
        coerce=int,
        error_messages={
            "required": "Elige una duración de 3, 7 o 14 días.",
            "invalid_choice": "Elige una duración válida.",
        },
        widget=forms.Select(attrs={"class": "campo"}),
    )
    q = forms.CharField(
        label="Título o autor",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "campo",
                "type": "search",
                "placeholder": "Ej.: Quijote o Cervantes",
                "autocomplete": "off",
            }
        ),
    )
    genero = forms.ChoiceField(
        label="Género",
        required=False,
        choices=[("", "Todos los géneros")],
        widget=forms.Select(attrs={"class": "campo"}),
    )
    solo_disponibles = forms.BooleanField(
        label="Solo disponibles",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "check"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["genero"].choices = [("", "Todos los géneros")] + [
            (genero, genero) for genero in services.generos_libros()
        ]


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
