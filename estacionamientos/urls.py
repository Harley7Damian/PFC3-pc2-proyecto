from django.urls import path

from . import views

app_name = "estacionamientos"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("nuevo/", views.nuevo, name="nuevo"),
]
