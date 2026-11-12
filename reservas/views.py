"""
Vistas de BibliotecaViva.

Cubre: RF-01, RF-02, RF-03, RF-04, RF-05, RF-07, RF-08.
"""
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from . import services
from .forms import (
    BusquedaForm,
    BusquedaLibrosForm,
    CodigoQRForm,
    PrestamoForm,
    ReservaForm,
)
from .models import Libro, Reserva, Recurso, Sancion, Usuario


def _es_bibliotecario(usuario):
    return usuario.rol == Usuario.Rol.BIBLIOTECARIO


def _fecha_legible(valor):
    """Normaliza una fecha ISO recibida por URL para mostrarla formateada."""
    if isinstance(valor, date):
        return valor
    if not valor:
        return None
    try:
        return date.fromisoformat(str(valor))
    except ValueError:
        return None


@login_required
def home(request):
    """Redirige según el rol del usuario (RF-08)."""
    if _es_bibliotecario(request.user):
        return redirect("bibliotecario")
    return redirect("buscar")


@login_required
def buscar(request):
    """Búsqueda de recursos por bloque o de libros por préstamo (RF-01)."""
    if _es_bibliotecario(request.user):
        return redirect("bibliotecario")

    vista = request.GET.get("vista", "recursos")
    hoy = services.hoy()
    sancion_hasta = (
        request.user.sancionado_hasta
        if request.user.esta_sancionado(services.ahora())
        else None
    )
    cupo = services.cupo_diario(request.user, hoy)

    if vista == "libros":
        form_libros = BusquedaLibrosForm(
            request.GET or None, initial={"fecha": hoy, "dias": 7}
        )
        tarjetas = None
        fecha_libros = hoy
        dias = 7
        if request.GET and form_libros.is_valid():
            fecha_libros = form_libros.cleaned_data["fecha"]
            dias = form_libros.cleaned_data["dias"]
            tarjetas = services.catalogo_libros(
                fecha_libros,
                form_libros.cleaned_data["q"],
                form_libros.cleaned_data["genero"],
                dias,
            )
        return render(
            request,
            "reservas/buscar.html",
            {
                "vista": "libros",
                "form_libros": form_libros,
                "tarjetas": tarjetas,
                "fecha": fecha_libros,
                "dias": dias,
                "cupo": cupo,
                "sancion_hasta": sancion_hasta,
                "prestamos": services.prestamos_activos(request.user),
                "max_prestamos": services.MAX_PRESTAMOS_ACTIVOS,
            },
        )

    bloques_hoy = services.bloques_disponibles(hoy)
    inicial = {
        "tipo": Recurso.Tipo.SALA,
        "fecha": hoy,
        "bloque": bloques_hoy[0][0] if bloques_hoy else "",
    }
    form = BusquedaForm(request.GET or None, initial=inicial)
    resultados = None
    fecha = None
    bloque = None
    fecha_consulta = _fecha_legible(request.GET.get("fecha")) or hoy
    if request.GET and form.is_valid():
        fecha_consulta = form.cleaned_data["fecha"]
    sin_bloques = not form["fecha"].errors and not services.bloques_disponibles(
        fecha_consulta
    )
    if request.GET and form.is_valid():
        fecha = form.cleaned_data["fecha"]
        bloque = form.cleaned_data["bloque"]
        resultados = services.recursos_disponibles(
            form.cleaned_data["tipo"], fecha, bloque
        )
    return render(
        request,
        "reservas/buscar.html",
        {
            "vista": "recursos",
            "form": form,
            "resultados": resultados,
            "fecha": fecha,
            "bloque": bloque,
            "cupo": cupo,
            "sancion_hasta": sancion_hasta,
            "sin_bloques": sin_bloques,
            "min_antelacion": services.MIN_ANTELACION_MIN,
            "max_dias": services.MAX_DIAS_RESERVA,
        },
    )


@login_required
def bloques(request):
    """Bloques disponibles para una fecha, para actualizar el filtro sin recargar."""
    fecha = _fecha_legible(request.GET.get("fecha"))
    if not fecha:
        return JsonResponse(
            {"error": "La fecha no es válida.", "bloques": []}, status=400
        )
    disponibles = services.bloques_disponibles(fecha)
    return JsonResponse(
        {
            "fecha": fecha.isoformat(),
            "bloques": [
                {"valor": valor, "etiqueta": etiqueta}
                for valor, etiqueta in disponibles
            ],
            "antelacion": services.MIN_ANTELACION_MIN,
            "horizonte": services.MAX_DIAS_RESERVA,
        }
    )


@login_required
def catalogo(request):
    """Compatibilidad: el catálogo vive ahora en la pestaña de libros."""
    return redirect(f"{reverse('buscar')}?vista=libros")


@login_required
def libro_detalle(request, libro_id):
    """Ficha bibliográfica y disponibilidad del préstamo (RF-01, RF-02)."""
    libro = get_object_or_404(Libro, pk=libro_id)
    hoy = services.hoy()
    form = PrestamoForm(
        request.GET or None, initial={"fecha": hoy, "dias": 7}
    )
    fecha = hoy
    dias = 7
    vencimiento = fecha + timedelta(days=dias)
    disponible = None
    if request.GET and form.is_valid():
        fecha = form.cleaned_data["fecha"]
        dias = form.cleaned_data["dias"]
        vencimiento = fecha + timedelta(days=dias)
        disponible = services.libro_disponible(libro, fecha, dias)
        if "continuar" in request.GET and disponible:
            return redirect(
                f"{reverse('confirmar', args=[libro.id])}"
                f"?fecha={fecha.isoformat()}&dias={dias}"
            )
    return render(
        request,
        "reservas/libro.html",
        {
            "libro": libro,
            "hoy": hoy,
            "form": form,
            "fecha": fecha,
            "dias": dias,
            "vencimiento": vencimiento,
            "disponible": disponible,
            "desde": services.proxima_disponibilidad(libro),
            "cupo": services.cupo_diario(request.user, hoy),
            "prestamos": services.prestamos_activos(request.user),
            "max_prestamos": services.MAX_PRESTAMOS_ACTIVOS,
            "sancion_hasta": (
                request.user.sancionado_hasta
                if request.user.esta_sancionado(services.ahora())
                else None
            ),
        },
    )


@login_required
def mis_reservas(request):
    """Lista las reservas del solicitante y permite reabrir su QR (RF-02, RF-03)."""
    if _es_bibliotecario(request.user):
        return redirect("bibliotecario")

    reservas = Reserva.objects.filter(usuario=request.user).select_related("recurso")
    activas = reservas.filter(
        estado__in=[Reserva.Estado.RESERVADA, Reserva.Estado.EN_USO]
    ).order_by("fecha", "bloque")
    historial = reservas.exclude(
        estado__in=[Reserva.Estado.RESERVADA, Reserva.Estado.EN_USO]
    ).order_by("-fecha", "-creada_en")
    return render(
        request,
        "reservas/mis_reservas.html",
        {"activas": activas, "historial": historial},
    )


@login_required
def confirmar(request, recurso_id):
    """Confirma una reserva por bloque o un préstamo de libro (RF-02, RF-03)."""
    if _es_bibliotecario(request.user):
        return redirect("bibliotecario")
    recurso = get_object_or_404(Recurso, pk=recurso_id)

    if recurso.tipo == Recurso.Tipo.LIBRO:
        if request.method == "POST":
            form = PrestamoForm(request.POST)
            if form.is_valid():
                try:
                    reserva = services.crear_reserva(
                        request.user,
                        recurso,
                        form.cleaned_data["fecha"],
                        dias=form.cleaned_data["dias"],
                    )
                except ValidationError as error:
                    messages.error(request, error.messages[0])
                    return redirect("libro", libro_id=recurso.id)
                return redirect("qr", reserva_id=reserva.pk)
            fecha = _fecha_legible(request.POST.get("fecha")) or services.hoy()
            try:
                dias = int(request.POST.get("dias") or 7)
            except (TypeError, ValueError):
                dias = 7
        else:
            fecha = _fecha_legible(request.GET.get("fecha")) or services.hoy()
            try:
                dias = int(request.GET.get("dias") or 7)
            except (TypeError, ValueError):
                dias = 7
            if not services.fecha_reservable(fecha) or not services.libro_disponible(
                recurso, fecha, dias
            ):
                messages.warning(
                    request,
                    "El libro no está disponible para ese rango de fechas. "
                    "Prueba con otra fecha o duración.",
                )
                return redirect("libro", libro_id=recurso.id)
            form = PrestamoForm(initial={"fecha": fecha, "dias": dias})
        return render(
            request,
            "reservas/confirmar.html",
            {
                "recurso": recurso,
                "form": form,
                "es_prestamo": True,
                "fecha": fecha,
                "dias": dias,
                "vencimiento": fecha + timedelta(days=dias),
            },
        )

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
        fecha = _fecha_legible(request.POST.get("fecha"))
        bloque = request.POST.get("bloque", "")
    else:
        fecha = _fecha_legible(request.GET.get("fecha")) or services.hoy()
        bloques_dia = services.bloques_disponibles(fecha)
        bloque = request.GET.get("bloque", "") or (
            bloques_dia[0][0] if bloques_dia else ""
        )
        if (
            bloque not in dict(Reserva.BLOQUES)
            or not services.fecha_reservable(fecha)
            or not services.bloque_vigente(bloque, fecha)
        ):
            messages.error(
                request,
                "El bloque seleccionado ya no está disponible. Elige otro horario.",
            )
            return redirect("buscar")
        form = ReservaForm(initial={"fecha": fecha, "bloque": bloque})
    return render(
        request,
        "reservas/confirmar.html",
        {
            "recurso": recurso,
            "form": form,
            "es_prestamo": False,
            "fecha": fecha,
            "bloque": bloque,
        },
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
        {
            "reserva": reserva,
            "qr": qr,
            "qr_img": services.qr_base64(qr.codigo),
            "cupo": services.cupo_diario(request.user, reserva.fecha),
        },
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

    hoy = services.hoy()
    reservas_dia = list(
        Reserva.objects.filter(
            Q(modalidad=Reserva.Modalidad.BLOQUE, fecha=hoy)
            | Q(
                modalidad=Reserva.Modalidad.PRESTAMO,
                fecha__lte=hoy,
                fecha_vencimiento__gte=hoy,
            )
        )
        .select_related("recurso", "usuario", "qr")
        .order_by("modalidad", "bloque", "recurso__nombre")
    )
    resumen = {
        "total": len(reservas_dia),
        "reservadas": sum(
            1 for r in reservas_dia if r.estado == Reserva.Estado.RESERVADA
        ),
        "en_uso": sum(1 for r in reservas_dia if r.estado == Reserva.Estado.EN_USO),
        "finalizadas": sum(
            1 for r in reservas_dia if r.estado == Reserva.Estado.FINALIZADA
        ),
    }
    resumen["porcentaje"] = (
        round(resumen["finalizadas"] * 100 / resumen["total"])
        if resumen["total"]
        else 0
    )
    sanciones_hoy = (
        Sancion.objects.filter(inicio__date=hoy)
        .select_related("usuario")
        .order_by("-inicio")[:3]
    )
    return render(
        request,
        "reservas/bibliotecario.html",
        {
            "form": form,
            "qr": qr,
            "reserva": reserva,
            "codigo": codigo,
            "hoy": hoy,
            "reservas_dia": reservas_dia,
            "resumen": resumen,
            "sanciones_hoy": sanciones_hoy,
            "inventario": services.estado_inventario(hoy),
        },
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
