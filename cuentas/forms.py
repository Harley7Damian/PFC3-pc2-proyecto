import re

from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

MENSAJE_INGRESO = "Correo o contraseña incorrectos."
PATRON_CORREO = re.compile(r"^[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$")
PATRON_NOMBRE = re.compile(r"^[^\W\d_][\w .'-]{1,59}$")


def normalizar_correo(valor):
    """Valida el correo en el servidor y lo devuelve en minúsculas, sin espacios."""
    correo = (valor or "").strip().lower()
    if len(correo) > 254 or not PATRON_CORREO.match(correo):
        raise ValidationError("Ingrese un correo electrónico válido.")
    return correo


class RegistroForm(forms.Form):
    nombre = forms.CharField(label="Nombre", max_length=60)
    correo = forms.EmailField(label="Correo electrónico", max_length=254)
    password1 = forms.CharField(label="Contraseña", strip=False, widget=forms.PasswordInput)
    password2 = forms.CharField(label="Repetir contraseña", strip=False, widget=forms.PasswordInput)

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if not PATRON_NOMBRE.match(nombre):
            raise ValidationError("Use solo letras, espacios, punto, guion o apóstrofe.")
        return nombre

    def clean_correo(self):
        correo = normalizar_correo(self.cleaned_data["correo"])
        if get_user_model().objects.filter(username__iexact=correo).exists():
            raise ValidationError("No fue posible registrar ese correo. Si ya tiene cuenta, inicie sesión.")
        return correo

    def clean(self):
        datos = super().clean()
        p1, p2 = datos.get("password1"), datos.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Las contraseñas no coinciden.")
        elif p1 and datos.get("correo"):
            usuario = get_user_model()(username=datos["correo"], email=datos["correo"],
                                       first_name=datos.get("nombre", ""))
            try:
                password_validation.validate_password(p1, usuario)
            except ValidationError as error:
                self.add_error("password1", error)
        return datos

    def guardar(self):
        datos = self.cleaned_data
        return get_user_model().objects.create_user(
            username=datos["correo"], email=datos["correo"], password=datos["password1"],
            first_name=datos["nombre"],
        )


class IngresoForm(AuthenticationForm):
    """Ingreso por correo con un único mensaje de error, sin revelar si la cuenta existe."""

    username = forms.CharField(label="Correo electrónico", max_length=254)
    error_messages = {"invalid_login": MENSAJE_INGRESO, "inactive": MENSAJE_INGRESO}

    def clean_username(self):
        return (self.cleaned_data["username"] or "").strip().lower()

    def clean(self):
        correo = self.cleaned_data.get("username")
        if correo and not PATRON_CORREO.match(correo):
            raise ValidationError(MENSAJE_INGRESO, code="invalid_login")
        return super().clean()
