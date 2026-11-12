"""
Modelo de datos de BibliotecaViva.

Cubre: RF-02, RF-04, RF-05, RF-07, RF-08.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Usuario(AbstractUser):
    """Usuario con rol y estado de sanción (RF-07, RF-08)."""

    class Rol(models.TextChoices):
        SOLICITANTE = "SOLICITANTE", "Solicitante"
        BIBLIOTECARIO = "BIBLIOTECARIO", "Bibliotecario"

    rol = models.CharField(
        max_length=20, choices=Rol.choices, default=Rol.SOLICITANTE
    )
    sancionado_hasta = models.DateTimeField(null=True, blank=True)

    def esta_sancionado(self, ahora=None):
        ahora = ahora or timezone.now()
        return bool(self.sancionado_hasta and self.sancionado_hasta > ahora)

    def __str__(self):
        return self.get_full_name() or self.username


class Recurso(models.Model):
    """Sala o equipo reservable (RF-01, RF-02)."""

    class Tipo(models.TextChoices):
        SALA = "SALA", "Sala"
        EQUIPO = "EQUIPO", "Equipo"
        LIBRO = "LIBRO", "Libro"

    class Estado(models.TextChoices):
        DISPONIBLE = "DISPONIBLE", "Disponible"
        NO_DISPONIBLE = "NO_DISPONIBLE", "No disponible"

    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    ubicacion = models.CharField(max_length=100, blank=True)
    capacidad = models.PositiveIntegerField(null=True, blank=True)
    codigo = models.CharField(max_length=20, blank=True)
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.DISPONIBLE
    )

    class Meta:
        ordering = ["tipo", "nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"


class Libro(Recurso):
    """Libro reservable con ficha bibliográfica y carátula local (RF-01, RF-02)."""

    autor = models.CharField(max_length=120)
    editorial = models.CharField(max_length=120, blank=True)
    anio = models.PositiveSmallIntegerField("año", null=True, blank=True)
    isbn = models.CharField("ISBN", max_length=20, blank=True)
    genero = models.CharField("género", max_length=60, blank=True)
    paginas = models.PositiveIntegerField("páginas", null=True, blank=True)
    sinopsis = models.TextField(blank=True)
    portada = models.CharField(
        max_length=200,
        blank=True,
        help_text="Ruta relativa dentro de static/reservas/.",
    )

    class Meta:
        ordering = ["nombre"]

    def save(self, *args, **kwargs):
        self.tipo = Recurso.Tipo.LIBRO
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} · {self.autor}"


class Reserva(models.Model):
    """Reserva de un recurso para una fecha y bloque (RF-02, RF-04, RF-05)."""

    class Estado(models.TextChoices):
        RESERVADA = "RESERVADA", "Reservada"
        EN_USO = "EN_USO", "En Uso"
        FINALIZADA = "FINALIZADA", "Finalizada"
        CANCELADA = "CANCELADA", "Cancelada"

    class Modalidad(models.TextChoices):
        BLOQUE = "BLOQUE", "Bloque horario"
        PRESTAMO = "PRESTAMO", "Préstamo de libro"

    BLOQUES = [
        (
            f"{hora:02d}:00-{hora + 1:02d}:00",
            f"{hora:02d}:00–{hora + 1:02d}:00",
        )
        for hora in range(9, 22)
    ]

    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name="reservas"
    )
    recurso = models.ForeignKey(
        Recurso, on_delete=models.CASCADE, related_name="reservas"
    )
    fecha = models.DateField()
    modalidad = models.CharField(
        max_length=20,
        choices=Modalidad.choices,
        default=Modalidad.BLOQUE,
    )
    bloque = models.CharField(max_length=20, choices=BLOQUES, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.RESERVADA
    )
    creada_en = models.DateTimeField(auto_now_add=True)
    iniciada_en = models.DateTimeField(null=True, blank=True)
    finalizada_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-creada_en"]
        constraints = [
            models.UniqueConstraint(
                fields=["recurso", "fecha", "bloque"],
                condition=models.Q(estado__in=["RESERVADA", "EN_USO"]),
                name="unique_recurso_fecha_bloque_activa",
            )
        ]

    def __str__(self):
        if self.modalidad == self.Modalidad.PRESTAMO:
            return (
                f"RSV-{self.pk:04d} · {self.recurso.nombre} · "
                f"{self.fecha} → {self.fecha_vencimiento}"
            )
        return f"RSV-{self.pk:04d} · {self.recurso.nombre} · {self.fecha} {self.bloque}"

    @property
    def codigo(self):
        return f"RSV-{self.pk:04d}"


class QR(models.Model):
    """Código QR asociado a una reserva (RF-03, RF-04)."""

    reserva = models.OneToOneField(
        Reserva, on_delete=models.CASCADE, related_name="qr"
    )
    codigo = models.CharField(max_length=20, unique=True)
    utilizado = models.BooleanField(default=False)
    generado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.codigo


class Sancion(models.Model):
    """Sanción por devolución tardía (RF-07)."""

    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name="sanciones"
    )
    reserva = models.OneToOneField(
        Reserva,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sancion",
    )
    inicio = models.DateTimeField()
    fin = models.DateTimeField()
    motivo = models.CharField(max_length=200, default="Devolución tardía")
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creada_en"]

    def __str__(self):
        return f"Sanción {self.usuario} hasta {self.fin:%Y-%m-%d}"
