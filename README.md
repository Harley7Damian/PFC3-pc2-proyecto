# CicloSeguro Lima

Aplicación web para ciclistas de Lima: consulta de rutas ciclistas con su nivel de seguridad, reporte de incidentes (robos, accidentes, vías en mal estado), panel de riesgo por distrito y catálogo de estacionamientos seguros para bicicletas. Proyecto de la Práctica Calificada 2 de Proyecto Final de Carrera III (USIL).

Los datos de rutas, incidentes y estacionamientos son ficticios y de demostración.

## Tecnología

Django 6 (monolito con cuatro aplicaciones: cuentas, rutas, incidentes y estacionamientos), PostgreSQL en producción y SQLite en local, WhiteNoise para los archivos estáticos, gunicorn en Render y django-axes para limitar intentos de ingreso.

## Ejecutar en local

```bash
python -m venv .venv
source .venv/Scripts/activate   # En Git Bash de Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py cargar_demo
python manage.py runserver
```

## Variables de entorno

| Variable | Uso |
| --- | --- |
| SECRET_KEY | Clave de Django. Obligatoria con DEBUG=0 |
| DEBUG | 1 en local (por defecto), 0 en producción |
| ALLOWED_HOSTS | Dominios permitidos, separados por comas |
| DATABASE_URL | Cadena de conexión de PostgreSQL. Sin ella se usa SQLite |
| ADMIN_EMAIL, ADMIN_PASSWORD | Opcionales: crean la cuenta de administración al desplegar |

Ninguna clave se guarda en el repositorio.

## Seguridad implementada

- Contraseñas con PBKDF2 y cuatro validadores (longitud mínima de 10, no comunes, no numéricas, no similares al correo).
- Correo validado en el servidor, único y en minúsculas. El ingreso muestra un único mensaje de error para correo inexistente o contraseña incorrecta.
- Bloqueo de 15 minutos tras 5 intentos fallidos (django-axes).
- CSRF activo, plantillas con escape automático, consultas por ORM, filtros validados contra listas cerradas.
- Cabeceras seguras, política de contenido (CSP) sin scripts ni estilos en línea, cookies seguras, HTTPS forzado y HSTS en producción.
- Pipeline con pruebas, cobertura, bandit, pip-audit, gitleaks, CodeQL, `check --deploy` y Dependabot.

## Ramas y flujo

`main` es producción y se despliega automáticamente. `test` es la rama de pruebas e integración. Cada tarjeta de Jira se trabaja en una rama `feature/PCF2-N-descripcion`, con pull request hacia `test`, y `test` se integra a `main` mediante pull request.
