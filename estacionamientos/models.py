from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from core.distritos import DISTRITOS


class Estacionamiento(models.Model):
    TIPOS = [
        ("publico_vigilado", "Público con vigilancia"),
        ("centro_comercial", "Centro comercial"),
        ("privado", "Privado o institucional"),
    ]

    nombre = models.CharField(max_length=120)
    distrito = models.CharField(max_length=20, choices=DISTRITOS)
    direccion = models.CharField(max_length=160)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    capacidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    vigilancia_24h = models.BooleanField(default=False)
    gratuito = models.BooleanField(default=True)
    registrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    # Los registros enviados por usuarios quedan pendientes hasta que la persona administradora los apruebe.
    aprobado = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["distrito", "nombre"]

    def __str__(self):
        return self.nombre
