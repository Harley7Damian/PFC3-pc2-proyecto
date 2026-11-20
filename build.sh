#!/usr/bin/env bash
# Comando de construcción para Render
set -o errexit
pip install -r requirements-prod.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py cargar_demo
python manage.py crear_admin
