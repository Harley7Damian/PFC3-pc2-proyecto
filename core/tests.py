import os
from io import StringIO
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from core.distritos import distrito_valido
from estacionamientos.models import Estacionamiento
from incidentes.models import Incidente
from rutas.models import Ruta


class CoreTests(TestCase):
    def test_inicio_responde(self):
        r = self.client.get(reverse("core:inicio"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "CicloSeguro Lima")

    def test_inicio_muestra_rutas_destacadas(self):
        call_command("cargar_demo", stdout=StringIO())
        r = self.client.get(reverse("core:inicio"))
        self.assertEqual(len(r.context["rutas_destacadas"]), 3)
        self.assertContains(r, "Rutas destacadas")
        self.assertContains(r, "Crear cuenta gratis")

    def test_inicio_para_usuario_con_sesion(self):
        usuario = get_user_model().objects.create_user("ana@example.com", "ana@example.com", "Bicicleta-Segura-2026")
        self.client.force_login(usuario)
        self.assertContains(self.client.get(reverse("core:inicio")), "Reportar un incidente")

    def test_salud(self):
        r = self.client.get(reverse("core:salud"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"estado": "ok"})

    def test_salud_sin_base_de_datos(self):
        with mock.patch("core.views.connection.ensure_connection", side_effect=Exception("sin base")):
            self.assertEqual(self.client.get(reverse("core:salud")).status_code, 503)

    def test_cabeceras_de_seguridad(self):
        r = self.client.get(reverse("core:inicio"))
        self.assertEqual(r["X-Frame-Options"], "DENY")
        self.assertEqual(r["X-Content-Type-Options"], "nosniff")
        self.assertIn("default-src 'self'", r["Content-Security-Policy"])

    def test_distrito_valido(self):
        self.assertEqual(distrito_valido("miraflores"), "miraflores")
        self.assertEqual(distrito_valido("otro"), "")

    def test_cargar_demo_es_idempotente(self):
        call_command("cargar_demo", stdout=StringIO())
        call_command("cargar_demo", stdout=StringIO())
        self.assertEqual(Ruta.objects.count(), 6)
        self.assertEqual(Incidente.objects.count(), 8)
        self.assertEqual(Estacionamiento.objects.count(), 5)

    def test_crear_admin(self):
        Usuario = get_user_model()
        call_command("crear_admin", stdout=StringIO())
        self.assertEqual(Usuario.objects.count(), 0)
        entorno = {"ADMIN_EMAIL": "Admin@Example.com", "ADMIN_PASSWORD": "Clave-De-Prueba-Admin-77"}
        with mock.patch.dict(os.environ, entorno):
            call_command("crear_admin", stdout=StringIO())
            call_command("crear_admin", stdout=StringIO())
        admin = Usuario.objects.get()
        self.assertTrue(admin.is_superuser)
        self.assertEqual(admin.username, "admin@example.com")
        self.assertTrue(admin.password.startswith("pbkdf2_sha256$"))
