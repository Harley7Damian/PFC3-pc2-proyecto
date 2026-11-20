# Ciclo DevSecOps de CicloSeguro Lima

## Herramientas y controles de seguridad por fase

| Fase | Herramientas | Control de seguridad integrado (shift-left) |
| --- | --- | --- |
| Plan | Jira: backlog, épicas, sprints y tablero Kanban | Los requisitos de seguridad son historias con criterios Dado/Cuando/Entonces (HU-01 registro seguro, HU-02 ingreso, HU-03 bloqueo, HU-10 moderación) y una tarea de endurecimiento (TR-05). |
| Code | Git y GitHub, ramas `main`, `test` y `feature/*`, plantilla de pull request | Rama `main` protegida con ruleset (pull request obligatorio, checks obligatorios, sin force push). `.gitignore` excluye `.env`. Plantilla de PR con lista de verificación de secretos y pruebas. |
| Build | GitHub Actions, pip, `build.sh` (collectstatic y migrate) | pip-audit revisa vulnerabilidades en las dependencias en cada pull request. gitleaks revisa secretos en todo el historial. |
| Test | `manage.py test` (48 pruebas unitarias y de integración), coverage con mínimo del 80 %, job con PostgreSQL, flake8 | Pruebas de seguridad: hash PBKDF2, correos y contraseñas inválidos, mensaje de error único, bloqueo tras 5 intentos, escape de HTML, control de acceso, filtros con valores maliciosos. SAST con bandit y CodeQL. |
| Release | Pull request de `test` a `main`, commit de fusión, Dependabot | Solo se fusiona con todos los checks en verde. Dependabot propone actualizaciones de dependencias y de acciones. |
| Deploy | Render, Neon (PostgreSQL con SSL), hook de despliegue desde GitHub Actions | Secretos solo en Render y en los secretos de GitHub. `DEBUG=0`. `check --deploy` sin advertencias en el pipeline. Despliegue solo desde `main` y solo con el pipeline en verde. |
| Operate | gunicorn, WhiteNoise, ruta `/salud/` | HTTPS forzado, HSTS, cookies seguras, CSP sin scripts en línea, X-Frame-Options, bloqueo por intentos fallidos (django-axes). |
| Monitor | Registros de Render, health check, pestaña Security de GitHub, alertas de Dependabot | Alertas de CodeQL y de dependencias. Los registros no incluyen contraseñas ni claves. Limitación: no hay APM ni alertas propias. |

## Etapas del pipeline (GitHub Actions)

| Flujo | Trabajo | Qué hace |
| --- | --- | --- |
| CI | Pruebas | Instala dependencias, ejecuta `check`, verifica que no falten migraciones y corre las pruebas. |
| CI | Calidad de código | Mide la cobertura (falla por debajo del 80 %) y revisa el estilo con flake8. |
| CI | Seguridad | pip-audit sobre las dependencias y bandit sobre el código (severidad media o alta). |
| CI | Pruebas contra PostgreSQL | Repite las pruebas en una base PostgreSQL real. |
| Seguridad | Secretos expuestos | gitleaks sobre todo el historial. |
| Seguridad | CodeQL | Análisis estático del código Python con consultas de seguridad ampliadas. |
| Seguridad | Configuración de producción | `check --deploy` con `DEBUG=0` y registro del resultado en el resumen. |
| CI | Despliegue a Render | Solo en `main`: solicita el despliegue con el hook y comprueba que la aplicación responde. |

## Justificación del stack según el caso

- **Django:** el caso exige cuentas, formularios y catálogos con datos de personas, y Django entrega autenticación, protección CSRF, escape de plantillas y ORM seguros por defecto, lo que permite construir rápido sin descuidar la seguridad.
- **PostgreSQL en Neon:** base relacional con SSL, gratuita y gestionada, adecuada para consultas por distrito y tipo.
- **Render:** despliegue gratuito con HTTPS, variables de entorno y despliegue desde GitHub.
- **GitHub Actions:** integra pruebas, análisis de seguridad y despliegue en el mismo repositorio donde se revisan los cambios.
- **Jira:** backlog, épicas, sprints y tablero que cubren la gestión Scrum pedida.
- **django-axes y CSP:** responden al riesgo principal del caso, que es proteger las cuentas y la información que reporta la comunidad.
