from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "cuentas"

urlpatterns = [
    path("registro/", views.registro, name="registro"),
    path("ingresar/", views.Ingresar.as_view(), name="ingresar"),
    path("salir/", LogoutView.as_view(), name="salir"),
]
