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

MAX_RESERVAS_DIA = 2


def ahora():
    """Hora de la aplicación; permite fijarla en modo demostración."""
    if settings.DEMO_MODE and settings.DEMO_NOW:
        valor = parse_datetime(settings.DEMO_NOW)
        if valor:
            if timezone.is_naive(valor):
                valor = timezone.make_aware(valor)
            return valor
    return timezone.now()


def hoy():
    """Fecha local de la aplicación; coherente con `ahora()` en modo demo."""
    return timezone.localtime(ahora()).date()


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


def cupo_diario(usuario, fecha=None):
    """Cupo diario del solicitante listo para la interfaz (RF-06)."""
    fecha = fecha or timezone.localdate()
    usadas = reservas_activas(usuario, fecha)
    restantes = max(0, MAX_RESERVAS_DIA - usadas)
    return {
        "usadas": usadas,
        "max": MAX_RESERVAS_DIA,
        "restantes": restantes,
        "porcentaje": round(usadas * 100 / MAX_RESERVAS_DIA),
    }


def crear_reserva(usuario, recurso, fecha, bloque):
    """Crea una reserva y su QR, validando sanción, tope y disponibilidad."""
    momento = ahora()
    if usuario.esta_sancionado(momento):
        raise ValidationError(
            "No puedes reservar: tienes una sanción vigente hasta "
            f"{timezone.localtime(usuario.sancionado_hasta):%d-%m-%Y %H:%M}."
        )
    if reservas_activas(usuario, fecha) >= MAX_RESERVAS_DIA:
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


def _estado_recurso(recurso, reservas):
    """Estado agregado de un recurso para la fecha consultada."""
    if recurso.estado != Recurso.Estado.DISPONIBLE:
        return "NO_DISPONIBLE", "No disponible"
    if any(reserva.estado == Reserva.Estado.EN_USO for reserva in reservas):
        return "EN_USO", "En uso"
    if reservas:
        return "RESERVADO", "Reservado"
    return "DISPONIBLE", "Disponible"


def estado_inventario(fecha):
    """Estado del inventario para el panel del bibliotecario (RF-04, RF-05).

    Agrupa por recurso el estado del día y por bloque; los totales permiten
    saber cuántos recursos están libres, reservados, en uso o fuera de servicio.
    """
    recursos = list(Recurso.objects.all())
    activas = Reserva.objects.filter(
        fecha=fecha,
        estado__in=[Reserva.Estado.RESERVADA, Reserva.Estado.EN_USO],
    ).select_related("usuario")
    por_recurso = {}
    for reserva in activas:
        por_recurso.setdefault(reserva.recurso_id, []).append(reserva)

    claves = {
        "DISPONIBLE": "disponibles",
        "RESERVADO": "reservados",
        "EN_USO": "en_uso",
        "NO_DISPONIBLE": "no_disponibles",
    }
    resumen = {
        "total": 0,
        "disponibles": 0,
        "reservados": 0,
        "en_uso": 0,
        "no_disponibles": 0,
    }
    por_tipo = {}
    filas = []

    for recurso in recursos:
        reservas = por_recurso.get(recurso.id, [])
        estado, etiqueta = _estado_recurso(recurso, reservas)

        fila = {"recurso": recurso, "estado": estado, "etiqueta": etiqueta, "bloques": []}
        reservas_por_bloque = {reserva.bloque: reserva for reserva in reservas}
        for valor, etiqueta_bloque in Reserva.BLOQUES:
            reserva = reservas_por_bloque.get(valor)
            if recurso.estado != Recurso.Estado.DISPONIBLE:
                estado_bloque = "NO_DISPONIBLE"
            elif reserva is None:
                estado_bloque = "DISPONIBLE"
            elif reserva.estado == Reserva.Estado.EN_USO:
                estado_bloque = "EN_USO"
            else:
                estado_bloque = "RESERVADO"
            fila["bloques"].append(
                {
                    "clave": valor,
                    "etiqueta": etiqueta_bloque,
                    "estado": estado_bloque,
                    "reserva": reserva,
                }
            )
        filas.append(fila)

        resumen["total"] += 1
        resumen[claves[estado]] += 1
        tipo = por_tipo.setdefault(
            recurso.tipo,
            {
                "tipo": recurso.tipo,
                "etiqueta": recurso.get_tipo_display(),
                "total": 0,
                "disponibles": 0,
                "reservados": 0,
                "en_uso": 0,
                "no_disponibles": 0,
            },
        )
        tipo["total"] += 1
        tipo[claves[estado]] += 1

    resumen["ocupados"] = resumen["reservados"] + resumen["en_uso"]
    resumen["porcentaje"] = (
        round(resumen["ocupados"] * 100 / resumen["total"]) if resumen["total"] else 0
    )
    return {
        "fecha": fecha,
        "bloques": Reserva.BLOQUES,
        "filas": filas,
        "resumen": resumen,
        "por_tipo": list(por_tipo.values()),
    }


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
