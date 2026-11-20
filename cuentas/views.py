from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from .forms import IngresoForm, RegistroForm


class Ingresar(LoginView):
    template_name = "cuentas/ingresar.html"
    authentication_form = IngresoForm
    redirect_authenticated_user = True


def registro(request):
    if request.user.is_authenticated:
        return redirect("core:inicio")
    formulario = RegistroForm(request.POST or None)
    if request.method == "POST" and formulario.is_valid():
        formulario.guardar()
        messages.success(request, "Cuenta creada. Ya puede iniciar sesión.")
        return redirect("cuentas:ingresar")
    return render(request, "cuentas/registro.html", {"formulario": formulario})
