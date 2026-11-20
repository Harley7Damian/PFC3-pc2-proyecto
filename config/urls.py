from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("cuentas/", include("cuentas.urls")),
    path("rutas/", include("rutas.urls")),
    path("incidentes/", include("incidentes.urls")),
    path("estacionamientos/", include("estacionamientos.urls")),
    path("", include("core.urls")),
]
