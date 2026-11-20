from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from core.distritos import DISTRITOS, distrito_valido

from .forms import EstacionamientoForm
from .models import Estacionamiento


def lista(request):
    distrito = distrito_valido(request.GET.get("distrito", ""))
    solo_vigilados = request.GET.get("vigilado") == "1"
    items = Estacionamiento.objects.filter(aprobado=True)
    if distrito:
        items = items.filter(distrito=distrito)
    if solo_vigilados:
        items = items.filter(vigilancia_24h=True)
    return render(request, "estacionamientos/lista.html", {
        "items": items, "distritos": DISTRITOS, "distrito": distrito, "solo_vigilados": solo_vigilados,
    })


@login_required
def nuevo(request):
    formulario = EstacionamientoForm(request.POST or None)
    if request.method == "POST" and formulario.is_valid():
        item = formulario.save(commit=False)
        item.registrado_por = request.user
        item.aprobado = False
        item.save()
        messages.success(request, "Registro enviado. Aparecerá en la lista cuando sea aprobado.")
        return redirect("estacionamientos:lista")
    return render(request, "estacionamientos/nuevo.html", {"formulario": formulario})
