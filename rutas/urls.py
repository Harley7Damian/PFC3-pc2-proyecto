from django.urls import path

from . import views

app_name = "rutas"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("<int:pk>/", views.detalle, name="detalle"),
    path("<int:pk>/calificar/", views.calificar, name="calificar"),
]
