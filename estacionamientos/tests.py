from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Estacionamiento

Usuario = get_user_model()


def crear_estacionamiento(**extra):
    datos = {"nombre": "Bicicletero central", "distrito": "miraflores", "direccion": "Parque central",
             "tipo": "publico_vigilado", "capacidad": 20, "vigilancia_24h": True, "aprobado": True}
    datos.update(extra)
    return Estacionamiento.objects.create(**datos)


class EstacionamientosTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user("ana@example.com", "ana@example.com", "Bicicleta-Segura-2026")

    def test_lista_muestra_solo_aprobados_y_filtra(self):
        crear_estacionamiento()
        crear_estacionamiento(nombre="Pendiente de revisión", aprobado=False)
        crear_estacionamiento(nombre="Sin vigilancia", distrito="surco", vigilancia_24h=False)
        r = self.client.get(reverse("estacionamientos:lista"))
        self.assertContains(r, "Bicicletero central")
        self.assertNotContains(r, "Pendiente de revisión")
        r = self.client.get(reverse("estacionamientos:lista"), {"vigilado": "1"})
        self.assertNotContains(r, "Sin vigilancia")
        r = self.client.get(reverse("estacionamientos:lista"), {"distrito": "surco"})
        self.assertContains(r, "Sin vigilancia")
        self.assertNotContains(r, "Bicicletero central")

    def test_registrar_exige_sesion(self):
        self.assertEqual(self.client.get(reverse("estacionamientos:nuevo")).status_code, 302)

    def test_registro_queda_pendiente(self):
        self.client.force_login(self.usuario)
        datos = {"nombre": "Nuevo bicicletero", "distrito": "lince", "direccion": "Av. Central 100",
                 "tipo": "privado", "capacidad": 10}
        self.assertEqual(self.client.get(reverse("estacionamientos:nuevo")).status_code, 200)
        r = self.client.post(reverse("estacionamientos:nuevo"), datos)
        self.assertRedirects(r, reverse("estacionamientos:lista"))
        nuevo = Estacionamiento.objects.get(nombre="Nuevo bicicletero")
        self.assertFalse(nuevo.aprobado)
        self.assertEqual(nuevo.registrado_por, self.usuario)
        self.assertNotContains(self.client.get(reverse("estacionamientos:lista")), "Nuevo bicicletero")

    def test_no_se_puede_auto_aprobar(self):
        self.client.force_login(self.usuario)
        datos = {"nombre": "Truco", "distrito": "lince", "direccion": "Av. Central 100", "tipo": "privado",
                 "capacidad": 10, "aprobado": "on"}
        self.client.post(reverse("estacionamientos:nuevo"), datos)
        self.assertFalse(Estacionamiento.objects.get(nombre="Truco").aprobado)

    def test_registro_invalido(self):
        self.client.force_login(self.usuario)
        r = self.client.post(reverse("estacionamientos:nuevo"), {"nombre": "", "capacidad": 0})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Estacionamiento.objects.count(), 0)

    def test_texto_del_modelo(self):
        self.assertEqual(str(crear_estacionamiento()), "Bicicletero central")
