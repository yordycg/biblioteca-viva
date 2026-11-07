"""
Vistas de BibliotecaViva.

Cubre: RF-01, RF-02, RF-03, RF-04, RF-05, RF-07, RF-08.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from . import services
from .forms import BusquedaForm, CodigoQRForm, ReservaForm
from .models import Reserva, Recurso, Usuario


def _es_bibliotecario(usuario):
    return usuario.rol == Usuario.Rol.BIBLIOTECARIO


@login_required
def home(request):
    """Redirige según el rol del usuario (RF-08)."""
    if _es_bibliotecario(request.user):
        return redirect("bibliotecario")
    return redirect("buscar")


@login_required
def buscar(request):
    """Búsqueda de recursos libres por tipo, fecha y bloque (RF-01)."""
    if _es_bibliotecario(request.user):
        return redirect("bibliotecario")

    inicial = {
        "tipo": Recurso.Tipo.SALA,
        "fecha": timezone.localdate(),
        "bloque": "10:00-11:00",
    }
    form = BusquedaForm(request.GET or None, initial=inicial)
    resultados = None
    fecha = None
    bloque = None
    if request.GET and form.is_valid():
        fecha = form.cleaned_data["fecha"]
        bloque = form.cleaned_data["bloque"]
        resultados = services.recursos_disponibles(
            form.cleaned_data["tipo"], fecha, bloque
        )
    return render(
        request,
        "reservas/buscar.html",
        {"form": form, "resultados": resultados, "fecha": fecha, "bloque": bloque},
    )


@login_required
def confirmar(request, recurso_id):
    """Muestra el detalle y crea la reserva con su QR (RF-02, RF-03, RF-06)."""
    if _es_bibliotecario(request.user):
        return redirect("bibliotecario")
    recurso = get_object_or_404(Recurso, pk=recurso_id)
    if request.method == "POST":
        form = ReservaForm(request.POST)
        if form.is_valid():
            try:
                reserva = services.crear_reserva(
                    request.user,
                    recurso,
                    form.cleaned_data["fecha"],
                    form.cleaned_data["bloque"],
                )
            except ValidationError as error:
                messages.error(request, error.messages[0])
                return redirect("buscar")
            return redirect("qr", reserva_id=reserva.pk)
    else:
        form = ReservaForm(
            initial={
                "fecha": request.GET.get("fecha", timezone.localdate()),
                "bloque": request.GET.get("bloque", "10:00-11:00"),
            }
        )
    return render(
        request, "reservas/confirmar.html", {"recurso": recurso, "form": form}
    )


@login_required
def qr_view(request, reserva_id):
    """Muestra el QR de una reserva confirmada (RF-03)."""
    reserva = get_object_or_404(Reserva, pk=reserva_id, usuario=request.user)
    qr = getattr(reserva, "qr", None)
    if not qr:
        messages.error(request, "La reserva no tiene un QR asociado.")
        return redirect("buscar")
    return render(
        request,
        "reservas/qr.html",
        {"reserva": reserva, "qr": qr, "qr_img": services.qr_base64(qr.codigo)},
    )


@login_required
def bibliotecario(request):
    """Vista del bibliotecario para validar inicio y devolución (RF-04, RF-05)."""
    if not _es_bibliotecario(request.user):
        return HttpResponseForbidden("Esta vista es solo para bibliotecarios.")

    codigo = request.GET.get("codigo", "")
    form = CodigoQRForm(request.GET or None)
    qr = None
    reserva = None
    if codigo:
        qr = services.obtener_por_codigo(codigo)
        if qr:
            reserva = qr.reserva
        else:
            messages.error(request, "QR inválido: no existe una reserva con ese código.")
    return render(
        request,
        "reservas/bibliotecario.html",
        {"form": form, "qr": qr, "reserva": reserva, "codigo": codigo},
    )


@login_required
@require_POST
def validar(request):
    """Confirma la entrega del recurso y pasa la reserva a En Uso (RF-04)."""
    if not _es_bibliotecario(request.user):
        return HttpResponseForbidden("Esta acción es solo para bibliotecarios.")
    codigo = request.POST.get("codigo", "")
    try:
        reserva = services.validar_inicio(codigo)
        messages.success(
            request,
            f"Entrega confirmada: {reserva.codigo} pasó a En Uso.",
        )
    except ValidationError as error:
        messages.error(request, error.messages[0])
    return redirect(f"{reverse('bibliotecario')}?codigo={codigo}")


@login_required
@require_POST
def devolver(request):
    """Registra la devolución y aplica la sanción si corresponde (RF-05, RF-07)."""
    if not _es_bibliotecario(request.user):
        return HttpResponseForbidden("Esta acción es solo para bibliotecarios.")
    codigo = request.POST.get("codigo", "")
    try:
        reserva, sancion = services.registrar_devolucion(codigo)
        if sancion:
            messages.warning(
                request,
                "Devolución tardía: se aplicó una sanción de 7 días a "
                f"{reserva.usuario.get_full_name() or reserva.usuario.username}.",
            )
        else:
            messages.success(
                request,
                f"Devolución registrada: {reserva.codigo} quedó Finalizada.",
            )
    except ValidationError as error:
        messages.error(request, error.messages[0])
    return redirect(f"{reverse('bibliotecario')}?codigo={codigo}")
