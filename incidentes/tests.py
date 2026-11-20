from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Incidente

Usuario = get_user_model()


def hoy():
    return timezone.localdate()


def crear_incidente(**extra):
    datos = {"tipo": "robo", "distrito": "miraflores", "descripcion": "Descripción del hecho",
             "fecha_hecho": hoy()}
    datos.update(extra)
    return Incidente.objects.create(**datos)


class IncidentesTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user("ana@example.com", "ana@example.com", "Bicicleta-Segura-2026")

    def datos(self, **cambios):
        datos = {"tipo": "robo", "distrito": "lince", "descripcion": "Intento de robo en el cruce",
                 "fecha_hecho": hoy().isoformat()}
        datos.update(cambios)
        return datos

    def test_lista_con_filtros(self):
        crear_incidente()
        crear_incidente(tipo="accidente", distrito="surco", descripcion="Choque en cruce")
        r = self.client.get(reverse("incidentes:lista"), {"distrito": "surco", "tipo": "accidente"})
        self.assertContains(r, "Choque en cruce")
        self.assertNotContains(r, "Descripción del hecho")

    def test_filtros_invalidos_se_ignoran(self):
        crear_incidente()
        r = self.client.get(reverse("incidentes:lista"), {"distrito": "' OR 1=1", "tipo": "<script>"})
        self.assertContains(r, "Descripción del hecho")

    def test_incidentes_ocultos_no_se_muestran(self):
        crear_incidente(visible=False, descripcion="Reporte oculto por moderación")
        self.assertNotContains(self.client.get(reverse("incidentes:lista")), "Reporte oculto")

    def test_reportar_exige_sesion(self):
        r = self.client.get(reverse("incidentes:nuevo"))
        self.assertEqual(r.status_code, 302)
        r = self.client.post(reverse("incidentes:nuevo"), self.datos())
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Incidente.objects.count(), 0)

    def test_reportar_guarda_con_la_persona_autora(self):
        self.client.force_login(self.usuario)
        r = self.client.post(reverse("incidentes:nuevo"), self.datos())
        self.assertRedirects(r, reverse("incidentes:lista"))
        self.assertEqual(Incidente.objects.get().reportado_por, self.usuario)
        self.assertEqual(self.client.get(reverse("incidentes:nuevo")).status_code, 200)

    def test_reporte_invalido_es_rechazado(self):
        self.client.force_login(self.usuario)
        malos = [self.datos(descripcion="corto"), self.datos(distrito="narnia"), self.datos(tipo="otro_tipo"),
                 self.datos(fecha_hecho=(hoy() + timedelta(days=2)).isoformat()), self.datos(fecha_hecho="ayer")]
        for datos in malos:
            r = self.client.post(reverse("incidentes:nuevo"), datos)
            self.assertEqual(r.status_code, 200)
        self.assertEqual(Incidente.objects.count(), 0)

    def test_descripcion_con_html_se_escapa(self):
        crear_incidente(descripcion="<script>alert(1)</script>")
        r = self.client.get(reverse("incidentes:lista"))
        self.assertNotContains(r, "<script>alert(1)</script>")
        self.assertContains(r, "&lt;script&gt;")

    def test_panel_ordena_por_riesgo(self):
        for _ in range(3):
            crear_incidente(distrito="lima")
        crear_incidente(distrito="surco", tipo="via_mal_estado")
        crear_incidente(distrito="lince", fecha_hecho=hoy() - timedelta(days=200))
        r = self.client.get(reverse("incidentes:panel"))
        datos = r.context["datos"]
        self.assertEqual([d["distrito"] for d in datos], ["Lima (Cercado)", "Santiago de Surco"])
        self.assertEqual(datos[0]["clase"], "alto")
        self.assertEqual(datos[1]["clase"], "bajo")

    def test_panel_vacio(self):
        self.assertContains(self.client.get(reverse("incidentes:panel")), "No hay incidentes recientes.")

    def test_texto_del_modelo(self):
        self.assertIn("Miraflores", str(crear_incidente()))


class PanelGraficoTests(TestCase):
    def test_dona_por_tipo_suma_cien(self):
        crear_incidente(tipo="robo")
        crear_incidente(tipo="robo", descripcion="Otro robo en la zona")
        crear_incidente(tipo="accidente", descripcion="Choque leve en el cruce")
        crear_incidente(tipo="invasion", descripcion="Vehículo sobre la ciclovía")
        r = self.client.get(reverse("incidentes:panel"))
        por_tipo = r.context["por_tipo"]
        self.assertEqual([t["tipo"] for t in por_tipo][0], "robo")
        self.assertAlmostEqual(sum(float(t["pct"]) for t in por_tipo), 100, delta=0.1)
        self.assertEqual(r.context["total"], 4)
        self.assertEqual(r.context["tipo_principal"], "Robo o intento de robo")
        self.assertContains(r, "stroke-dasharray")
        self.assertNotContains(r, "stroke-dasharray=\"50,00")

    def test_panel_sin_datos_no_muestra_dona(self):
        r = self.client.get(reverse("incidentes:panel"))
        self.assertEqual(r.context["por_tipo"], [])
        self.assertNotContains(r, "dona-seg")
