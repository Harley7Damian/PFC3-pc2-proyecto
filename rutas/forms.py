from django import forms

from .models import Calificacion


class CalificacionForm(forms.ModelForm):
    puntaje = forms.TypedChoiceField(
        label="Puntaje", coerce=int, choices=[(i, "%d" % i) for i in range(1, 6)], widget=forms.RadioSelect,
        error_messages={"required": "Elige un puntaje de 1 a 5.", "invalid_choice": "Elige un puntaje de 1 a 5."},
    )

    class Meta:
        model = Calificacion
        fields = ["puntaje", "comentario"]
