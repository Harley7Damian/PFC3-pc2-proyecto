from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from core.distritos import DISTRITOS, distrito_valido

from .forms import CalificacionForm
from .models import Calificacion, Ruta


def lista(request):
    distrito = distrito_valido(request.GET.get("distrito", ""))
    rutas = Ruta.objects.filter(activa=True)
    if distrito:
        rutas = [r for r in rutas if distrito in (r.distrito_origen, r.distrito_destino)]
    return render(request, "rutas/lista.html", {"rutas": rutas, "distritos": DISTRITOS, "distrito": distrito})


def detalle(request, pk):
    ruta = get_object_or_404(Ruta, pk=pk, activa=True)
    formulario = CalificacionForm()
    return render(request, "rutas/detalle.html", {
        "ruta": ruta, "formulario": formulario, "calificaciones": ruta.calificaciones.select_related("usuario")[:10],
    })


@login_required
def calificar(request, pk):
    ruta = get_object_or_404(Ruta, pk=pk, activa=True)
    if request.method != "POST":
        return redirect("rutas:detalle", pk=ruta.pk)
    formulario = CalificacionForm(request.POST)
    if formulario.is_valid():
        Calificacion.objects.update_or_create(
            ruta=ruta, usuario=request.user, defaults=formulario.cleaned_data,
        )
        messages.success(request, "Gracias por calificar la ruta.")
        return redirect("rutas:detalle", pk=ruta.pk)
    return render(request, "rutas/detalle.html", {
        "ruta": ruta, "formulario": formulario, "calificaciones": ruta.calificaciones.select_related("usuario")[:10],
    })
