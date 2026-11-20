from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Incidente


class IncidenteForm(forms.ModelForm):
    class Meta:
        model = Incidente
        fields = ["tipo", "distrito", "descripcion", "fecha_hecho"]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3}),
            "fecha_hecho": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_descripcion(self):
        texto = self.cleaned_data["descripcion"].strip()
        if len(texto) < 10:
            raise ValidationError("Describa el hecho con al menos 10 caracteres.")
        return texto

    def clean_fecha_hecho(self):
        fecha = self.cleaned_data["fecha_hecho"]
        if fecha > timezone.localdate():
            raise ValidationError("La fecha no puede ser futura.")
        return fecha
