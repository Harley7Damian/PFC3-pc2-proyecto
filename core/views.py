from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render

from estacionamientos.models import Estacionamiento
from incidentes.models import Incidente
from rutas.models import Ruta


def inicio(request):
    rutas = sorted(Ruta.objects.filter(activa=True), key=lambda r: r.nivel_seguridad(), reverse=True)
    contexto = {
        "rutas_destacadas": rutas[:3],
        "total_rutas": Ruta.objects.filter(activa=True).count(),
        "total_incidentes": Incidente.objects.filter(visible=True).count(),
        "total_estacionamientos": Estacionamiento.objects.filter(aprobado=True).count(),
    }
    return render(request, "inicio.html", contexto)


def salud(request):
    """Comprobación de estado para Render y para el pipeline: confirma que hay base de datos."""
    try:
        connection.ensure_connection()
    except Exception:
        return JsonResponse({"estado": "error"}, status=503)
    return JsonResponse({"estado": "ok"})
