from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import redirect, render
from django.utils import timezone

from core.distritos import DISTRITOS, distrito_valido

from .forms import IncidenteForm
from .models import Incidente

TIPOS_VALIDOS = {clave for clave, _ in Incidente.TIPOS}
DIAS_PANEL = 90


def lista(request):
    distrito = distrito_valido(request.GET.get("distrito", ""))
    tipo = request.GET.get("tipo", "")
    tipo = tipo if tipo in TIPOS_VALIDOS else ""
    incidentes = Incidente.objects.filter(visible=True)
    if distrito:
        incidentes = incidentes.filter(distrito=distrito)
    if tipo:
        incidentes = incidentes.filter(tipo=tipo)
    return render(request, "incidentes/lista.html", {
        "incidentes": incidentes[:100], "distritos": DISTRITOS, "tipos": Incidente.TIPOS,
        "distrito": distrito, "tipo": tipo,
    })


@login_required
def nuevo(request):
    formulario = IncidenteForm(request.POST or None)
    if request.method == "POST" and formulario.is_valid():
        incidente = formulario.save(commit=False)
        incidente.reportado_por = request.user
        incidente.save()
        messages.success(request, "Reporte registrado. Gracias por avisar a la comunidad.")
        return redirect("incidentes:lista")
    return render(request, "incidentes/nuevo.html", {"formulario": formulario})


def nivel_riesgo(puntos):
    if puntos >= 6:
        return "alto", "Riesgo alto"
    if puntos >= 3:
        return "medio", "Riesgo medio"
    return "bajo", "Riesgo bajo"


def panel(request):
    """Riesgo por distrito: robos y accidentes pesan 3 puntos; el resto, 1 punto (últimos 90 días)."""
    desde = timezone.localdate() - timedelta(days=DIAS_PANEL)
    filas = (
        Incidente.objects.filter(visible=True, fecha_hecho__gte=desde)
        .values("distrito")
        .annotate(
            total=Count("id"),
            graves=Count("id", filter=Q(tipo__in=["robo", "accidente"])),
        )
    )
    nombres = dict(DISTRITOS)
    datos = []
    for fila in filas:
        puntos = fila["graves"] * 3 + (fila["total"] - fila["graves"])
        clase, etiqueta = nivel_riesgo(puntos)
        datos.append({"distrito": nombres.get(fila["distrito"], fila["distrito"]), "total": fila["total"],
                      "puntos": puntos, "clase": clase, "etiqueta": etiqueta})
    datos.sort(key=lambda d: d["puntos"], reverse=True)
    maximo = datos[0]["puntos"] if datos else 1
    for d in datos:
        d["ancho"] = max(5, round(d["puntos"] * 100 / maximo))
    return render(request, "incidentes/panel.html", {"datos": datos, "dias": DIAS_PANEL})
