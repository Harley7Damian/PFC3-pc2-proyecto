from django import forms

from .models import Estacionamiento


class EstacionamientoForm(forms.ModelForm):
    class Meta:
        model = Estacionamiento
        fields = ["nombre", "distrito", "direccion", "tipo", "capacidad", "vigilancia_24h", "gratuito"]
