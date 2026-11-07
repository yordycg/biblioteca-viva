"""
Reglas de negocio de BibliotecaViva.

Cubre: RF-01, RF-02, RF-03, RF-04, RF-05, RF-06, RF-07.
"""
import base64
from datetime import datetime, time, timedelta
from io import BytesIO

import qrcode
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from .models import QR, Reserva, Recurso, Sancion


def ahora():
    """Hora de la aplicación; permite fijarla en modo demostración."""
    if settings.DEMO_MODE and settings.DEMO_NOW:
        valor = parse_datetime(settings.DEMO_NOW)
        if valor:
            if timezone.is_naive(valor):
                valor = timezone.make_aware(valor)
            return valor
    return timezone.now()


def bloque_horas(bloque):
    """Devuelve (hora_inicio, hora_fin) de un bloque 'HH:MM-HH:MM'."""
    inicio, fin = bloque.split("-")
    return time(int(inicio[:2]), int(inicio[3:])), time(int(fin[:2]), int(fin[3:]))


def recursos_disponibles(tipo, fecha, bloque):
    """Recursos libres para un tipo, fecha y bloque (RF-01)."""
    ocupados = Reserva.objects.filter(
        fecha=fecha,
        bloque=bloque,
        estado__in=[Reserva.Estado.RESERVADA, Reserva.Estado.EN_USO],
    ).values_list("recurso_id", flat=True)
    return Recurso.objects.filter(
        tipo=tipo, estado=Recurso.Estado.DISPONIBLE
    ).exclude(id__in=ocupados)


def reservas_activas(usuario, fecha):
    """Cantidad de reservas activas del usuario en la fecha (RF-06)."""
    return Reserva.objects.filter(
        usuario=usuario,
        fecha=fecha,
        estado__in=[Reserva.Estado.RESERVADA, Reserva.Estado.EN_USO],
    ).count()


def crear_reserva(usuario, recurso, fecha, bloque):
    """Crea una reserva y su QR, validando sanción, tope y disponibilidad."""
    momento = ahora()
    if usuario.esta_sancionado(momento):
        raise ValidationError(
            "No puedes reservar: tienes una sanción vigente hasta "
            f"{timezone.localtime(usuario.sancionado_hasta):%d-%m-%Y %H:%M}."
        )
    if reservas_activas(usuario, fecha) >= 2:
        raise ValidationError(
            "Límite alcanzado: ya tienes 2 reservas activas para ese día."
        )
    if recurso.estado != Recurso.Estado.DISPONIBLE:
        raise ValidationError("El recurso no está disponible.")
    if Reserva.objects.filter(
        recurso=recurso,
        fecha=fecha,
        bloque=bloque,
        estado__in=[Reserva.Estado.RESERVADA, Reserva.Estado.EN_USO],
    ).exists():
        raise ValidationError("El recurso ya está reservado para ese bloque.")

    try:
        with transaction.atomic():
            reserva = Reserva.objects.create(
                usuario=usuario,
                recurso=recurso,
                fecha=fecha,
                bloque=bloque,
                estado=Reserva.Estado.RESERVADA,
            )
            QR.objects.create(reserva=reserva, codigo=reserva.codigo)
    except IntegrityError:
        raise ValidationError("El recurso ya está reservado para ese bloque.")
    return reserva


def obtener_por_codigo(codigo):
    """Busca una reserva por el código del QR."""
    codigo = (codigo or "").strip().upper()
    return (
        QR.objects.select_related("reserva", "reserva__recurso", "reserva__usuario")
        .filter(codigo=codigo)
        .first()
    )


def validar_inicio(codigo, momento=None):
    """Valida el QR y pasa la reserva a En Uso (RF-04)."""
    momento = momento or ahora()
    qr = obtener_por_codigo(codigo)
    if not qr:
        raise ValidationError("QR inválido: no existe una reserva con ese código.")
    if qr.utilizado or qr.reserva.estado != Reserva.Estado.RESERVADA:
        raise ValidationError("QR ya utilizado o la reserva no está vigente.")

    if not settings.DEMO_MODE:
        if qr.reserva.fecha != timezone.localdate(momento):
            raise ValidationError("La reserva no corresponde a la fecha de hoy.")
        inicio, fin = bloque_horas(qr.reserva.bloque)
        inicio_dt = timezone.make_aware(
            datetime.combine(qr.reserva.fecha, inicio)
        ) - timedelta(minutes=15)
        fin_dt = timezone.make_aware(datetime.combine(qr.reserva.fecha, fin))
        if not (inicio_dt <= momento <= fin_dt):
            raise ValidationError("Fuera del horario del bloque reservado.")

    qr.utilizado = True
    qr.reserva.estado = Reserva.Estado.EN_USO
    qr.reserva.iniciada_en = momento
    qr.save(update_fields=["utilizado"])
    qr.reserva.save(update_fields=["estado", "iniciada_en"])
    return qr.reserva


def registrar_devolucion(codigo, momento=None):
    """Registra la devolución y aplica sanción si es tardía (RF-05, RF-07)."""
    momento = momento or ahora()
    qr = obtener_por_codigo(codigo)
    if not qr:
        raise ValidationError("QR inválido: no existe una reserva con ese código.")
    reserva = qr.reserva
    if reserva.estado != Reserva.Estado.EN_USO:
        raise ValidationError("La reserva no está En Uso; no se puede devolver.")

    reserva.estado = Reserva.Estado.FINALIZADA
    reserva.finalizada_en = momento
    reserva.save(update_fields=["estado", "finalizada_en"])

    _, fin_bloque = bloque_horas(reserva.bloque)
    limite = timezone.make_aware(datetime.combine(reserva.fecha, fin_bloque))
    sancion = None
    if momento > limite:
        fin_sancion = momento + timedelta(days=7)
        sancion = Sancion.objects.create(
            usuario=reserva.usuario,
            reserva=reserva,
            inicio=momento,
            fin=fin_sancion,
            motivo="Devolución tardía",
        )
        usuario = reserva.usuario
        if not usuario.sancionado_hasta or usuario.sancionado_hasta < fin_sancion:
            usuario.sancionado_hasta = fin_sancion
            usuario.save(update_fields=["sancionado_hasta"])
    return reserva, sancion


def qr_base64(codigo):
    """Genera la imagen PNG del QR y la devuelve como data URI."""
    imagen = qrcode.make(codigo)
    buffer = BytesIO()
    imagen.save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()
