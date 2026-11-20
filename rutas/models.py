from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg

from core.distritos import DISTRITOS


class Ruta(models.Model):
    ESTADOS = [
        ("segregada", "Ciclovía exclusiva"),
        ("parcial", "Ciclovía parcial o compartida"),
        ("sin_ciclovia", "Sin ciclovía"),
    ]

    nombre = models.CharField(max_length=120, unique=True)
    distrito_origen = models.CharField(max_length=20, choices=DISTRITOS)
    distrito_destino = models.CharField(max_length=20, choices=DISTRITOS)
    longitud_km = models.DecimalField(max_digits=5, decimal_places=1, validators=[MinValueValidator(0)])
    estado_ciclovia = models.CharField(max_length=20, choices=ESTADOS)
    descripcion = models.TextField(max_length=500, blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def puntaje_promedio(self):
        return self.calificaciones.aggregate(p=Avg("puntaje"))["p"]

    def nivel_seguridad(self):
        """Nivel de 1 a 3 según el estado de la ciclovía y el puntaje de los usuarios."""
        base = {"segregada": 3, "parcial": 2, "sin_ciclovia": 1}[self.estado_ciclovia]
        promedio = self.puntaje_promedio()
        if promedio is None:
            return base
        if promedio >= 4:
            return min(3, base + 1)
        if promedio < 2.5:
            return max(1, base - 1)
        return base

    def etiqueta_nivel(self):
        return {1: "Precaución", 2: "Aceptable", 3: "Segura"}[self.nivel_seguridad()]


class Calificacion(models.Model):
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE, related_name="calificaciones")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    puntaje = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.CharField(max_length=300, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["ruta", "usuario"], name="una_calificacion_por_usuario")]
        ordering = ["-creado_en"]

    def __str__(self):
        return "%s: %s" % (self.ruta, self.puntaje)
