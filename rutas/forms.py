from django import forms

from .models import Calificacion


class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = ["puntaje", "comentario"]
        widgets = {"puntaje": forms.NumberInput(attrs={"min": 1, "max": 5})}
