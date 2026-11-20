from django.conf import settings
from django.db import models

from core.distritos import DISTRITOS


class Incidente(models.Model):
    TIPOS = [
        ("robo", "Robo o intento de robo"),
        ("accidente", "Accidente"),
        ("via_mal_estado", "Vía en mal estado"),
        ("invasion", "Ciclovía invadida"),
        ("otro", "Otro"),
    ]

    tipo = models.CharField(max_length=20, choices=TIPOS)
    distrito = models.CharField(max_length=20, choices=DISTRITOS)
    descripcion = models.CharField(max_length=500)
    fecha_hecho = models.DateField()
    reportado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    creado_en = models.DateTimeField(auto_now_add=True)
    # La persona administradora puede ocultar un reporte indebido (moderación).
    visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["-fecha_hecho", "-creado_en"]

    def __str__(self):
        return "%s en %s (%s)" % (self.get_tipo_display(), self.get_distrito_display(), self.fecha_hecho)
