"""Crea el usuario administrador a partir de variables de entorno (ADMIN_EMAIL, ADMIN_PASSWORD).

No hace nada si faltan las variables o si el usuario ya existe. La contraseña nunca va en el repositorio.
"""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crea el administrador desde ADMIN_EMAIL y ADMIN_PASSWORD si no existe."

    def handle(self, *args, **opciones):
        correo = os.environ.get("ADMIN_EMAIL", "").strip().lower()
        clave = os.environ.get("ADMIN_PASSWORD", "")
        if not correo or not clave:
            self.stdout.write("Sin ADMIN_EMAIL o ADMIN_PASSWORD: no se crea administrador.")
            return
        Usuario = get_user_model()
        if Usuario.objects.filter(username=correo).exists():
            self.stdout.write("El administrador ya existe.")
            return
        Usuario.objects.create_superuser(username=correo, email=correo, password=clave)
        self.stdout.write("Administrador creado.")
