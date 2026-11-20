from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

Usuario = get_user_model()
CLAVE_BUENA = "Bicicleta-Segura-2026"


def datos_registro(**cambios):
    datos = {"nombre": "Ana Pérez", "correo": "ana@example.com", "password1": CLAVE_BUENA, "password2": CLAVE_BUENA}
    datos.update(cambios)
    return datos


class RegistroTests(TestCase):
    def test_registro_valido_guarda_la_contrasena_hasheada(self):
        r = self.client.post(reverse("cuentas:registro"), datos_registro())
        self.assertRedirects(r, reverse("cuentas:ingresar"))
        usuario = Usuario.objects.get(username="ana@example.com")
        self.assertNotEqual(usuario.password, CLAVE_BUENA)
        self.assertTrue(usuario.password.startswith("pbkdf2_sha256$"))
        self.assertTrue(usuario.check_password(CLAVE_BUENA))

    def test_correo_se_guarda_en_minusculas(self):
        self.client.post(reverse("cuentas:registro"), datos_registro(correo="  ANA@Example.COM "))
        self.assertTrue(Usuario.objects.filter(username="ana@example.com").exists())

    def test_correos_invalidos_son_rechazados(self):
        malos = ["", "ana", "ana@", "@example.com", "ana@example", "ana@@example.com", "ana example@x.com",
                 "ana@example..com", "ana@-.com", "<script>alert(1)</script>@x.com", "ana@x.com'; DROP TABLE auth_user;--",
                 "a" * 70 + "@example.com", "ana@example.c"]
        for correo in malos:
            with self.subTest(correo=correo):
                r = self.client.post(reverse("cuentas:registro"), datos_registro(correo=correo))
                self.assertEqual(r.status_code, 200)
                self.assertEqual(Usuario.objects.count(), 0)

    def test_correo_duplicado_sin_distinguir_mayusculas(self):
        self.client.post(reverse("cuentas:registro"), datos_registro())
        r = self.client.post(reverse("cuentas:registro"), datos_registro(correo="ANA@example.com"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Usuario.objects.count(), 1)

    def test_contrasenas_debiles_son_rechazadas(self):
        for clave in ["corta1", "1234567890", "password123", "contrasena", "ana@example.com", "Ana Pérez"]:
            with self.subTest(clave=clave):
                r = self.client.post(reverse("cuentas:registro"), datos_registro(password1=clave, password2=clave))
                self.assertEqual(r.status_code, 200)
                self.assertEqual(Usuario.objects.count(), 0)

    def test_contrasenas_distintas(self):
        r = self.client.post(reverse("cuentas:registro"), datos_registro(password2="Otra-Clave-Distinta-1"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Usuario.objects.count(), 0)

    def test_nombre_con_html_es_rechazado(self):
        r = self.client.post(reverse("cuentas:registro"), datos_registro(nombre="<b>Ana</b>"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Usuario.objects.count(), 0)

    def test_campos_vacios(self):
        r = self.client.post(reverse("cuentas:registro"), {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Usuario.objects.count(), 0)

    def test_usuario_con_sesion_no_ve_el_registro(self):
        Usuario.objects.create_user("ana@example.com", "ana@example.com", CLAVE_BUENA)
        self.client.force_login(Usuario.objects.get(username="ana@example.com"))
        self.assertRedirects(self.client.get(reverse("cuentas:registro")), reverse("core:inicio"))


class IngresoTests(TestCase):
    def setUp(self):
        Usuario.objects.create_user("ana@example.com", "ana@example.com", CLAVE_BUENA, first_name="Ana")

    def ingresar(self, correo, clave):
        return self.client.post(reverse("cuentas:ingresar"), {"username": correo, "password": clave})

    def test_ingreso_valido(self):
        r = self.ingresar("ana@example.com", CLAVE_BUENA)
        self.assertRedirects(r, reverse("core:inicio"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_ingreso_acepta_mayusculas_en_el_correo(self):
        r = self.ingresar("ANA@Example.com", CLAVE_BUENA)
        self.assertEqual(r.status_code, 302)

    def test_contrasena_incorrecta_y_correo_inexistente_dan_el_mismo_mensaje(self):
        mal_clave = self.ingresar("ana@example.com", "Clave-Incorrecta-9")
        inexistente = self.ingresar("nadie@example.com", CLAVE_BUENA)
        for r in (mal_clave, inexistente):
            self.assertEqual(r.status_code, 200)
            self.assertNotIn("_auth_user_id", self.client.session)
            self.assertContains(r, "Correo o contraseña incorrectos.")

    def test_entradas_basura_no_inician_sesion(self):
        basura = [("", ""), ("ana", CLAVE_BUENA), ("ana@example.com", ""), ("' OR '1'='1", "' OR '1'='1"),
                  ("<script>alert(1)</script>", "x"), ("ana@example.com' --", CLAVE_BUENA),
                  ("ana@example.com", "' OR '1'='1"), ("admin", "admin")]
        for correo, clave in basura:
            with self.subTest(correo=correo):
                r = self.ingresar(correo, clave)
                self.assertEqual(r.status_code, 200)
                self.assertNotIn("_auth_user_id", self.client.session)

    def test_cuenta_inactiva_no_ingresa_y_no_se_distingue(self):
        Usuario.objects.filter(username="ana@example.com").update(is_active=False)
        r = self.ingresar("ana@example.com", CLAVE_BUENA)
        self.assertContains(r, "Correo o contraseña incorrectos.")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_bloqueo_tras_cinco_intentos_fallidos(self):
        for _ in range(5):
            self.ingresar("ana@example.com", "Clave-Incorrecta-9")
        r = self.ingresar("ana@example.com", CLAVE_BUENA)
        self.assertEqual(r.status_code, 429)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_salir_exige_post(self):
        self.ingresar("ana@example.com", CLAVE_BUENA)
        self.assertEqual(self.client.get(reverse("cuentas:salir")).status_code, 405)
        self.assertIn("_auth_user_id", self.client.session)
        self.client.post(reverse("cuentas:salir"))
        self.assertNotIn("_auth_user_id", self.client.session)
