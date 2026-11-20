from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Calificacion, Ruta

Usuario = get_user_model()


def crear_ruta(**extra):
    datos = {"nombre": "Ruta de prueba", "distrito_origen": "miraflores", "distrito_destino": "barranco",
             "longitud_km": "4.2", "estado_ciclovia": "segregada", "descripcion": "Descripción"}
    datos.update(extra)
    return Ruta.objects.create(**datos)


class RutasTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user("ana@example.com", "ana@example.com", "Bicicleta-Segura-2026")

    def test_lista_y_filtro_por_distrito(self):
        crear_ruta()
        crear_ruta(nombre="Otra ruta", distrito_origen="surco", distrito_destino="surquillo")
        self.assertContains(self.client.get(reverse("rutas:lista")), "Otra ruta")
        r = self.client.get(reverse("rutas:lista"), {"distrito": "barranco"})
        self.assertContains(r, "Ruta de prueba")
        self.assertNotContains(r, "Otra ruta")

    def test_filtro_malicioso_se_ignora(self):
        crear_ruta()
        r = self.client.get(reverse("rutas:lista"), {"distrito": "x' OR 1=1 --"})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Ruta de prueba")

    def test_rutas_inactivas_no_se_muestran(self):
        ruta = crear_ruta(activa=False)
        self.assertNotContains(self.client.get(reverse("rutas:lista")), "Ruta de prueba")
        self.assertEqual(self.client.get(reverse("rutas:detalle", args=[ruta.pk])).status_code, 404)

    def test_detalle_escapa_html(self):
        ruta = crear_ruta(descripcion="<script>alert(1)</script>")
        r = self.client.get(reverse("rutas:detalle", args=[ruta.pk]))
        self.assertNotContains(r, "<script>alert(1)</script>")
        self.assertContains(r, "&lt;script&gt;")

    def test_calificar_exige_sesion(self):
        ruta = crear_ruta()
        r = self.client.post(reverse("rutas:calificar", args=[ruta.pk]), {"puntaje": 5, "comentario": "Bien"})
        self.assertEqual(r.status_code, 302)
        self.assertIn("/cuentas/ingresar/", r["Location"])
        self.assertEqual(Calificacion.objects.count(), 0)

    def test_calificar_guarda_y_actualiza(self):
        ruta = crear_ruta()
        self.client.force_login(self.usuario)
        self.client.post(reverse("rutas:calificar", args=[ruta.pk]), {"puntaje": 5, "comentario": "Bien"})
        self.client.post(reverse("rutas:calificar", args=[ruta.pk]), {"puntaje": 4, "comentario": "Casi"})
        self.assertEqual(Calificacion.objects.count(), 1)
        self.assertEqual(ruta.puntaje_promedio(), 4)

    def test_puntaje_fuera_de_rango_es_rechazado(self):
        ruta = crear_ruta()
        self.client.force_login(self.usuario)
        for puntaje in ["0", "6", "abc", ""]:
            r = self.client.post(reverse("rutas:calificar", args=[ruta.pk]), {"puntaje": puntaje})
            self.assertEqual(r.status_code, 200)
        self.assertEqual(Calificacion.objects.count(), 0)

    def test_calificar_por_get_redirige(self):
        ruta = crear_ruta()
        self.client.force_login(self.usuario)
        self.assertEqual(self.client.get(reverse("rutas:calificar", args=[ruta.pk])).status_code, 302)

    def test_nivel_de_seguridad(self):
        ruta = crear_ruta(estado_ciclovia="parcial")
        self.assertEqual(ruta.nivel_seguridad(), 2)
        self.assertEqual(ruta.etiqueta_nivel(), "Aceptable")
        Calificacion.objects.create(ruta=ruta, usuario=self.usuario, puntaje=5)
        self.assertEqual(ruta.nivel_seguridad(), 3)
        Calificacion.objects.filter(ruta=ruta).update(puntaje=1)
        self.assertEqual(ruta.nivel_seguridad(), 1)
        self.assertEqual(str(ruta), "Ruta de prueba")
