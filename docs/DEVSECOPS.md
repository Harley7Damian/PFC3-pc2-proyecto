# Ciclo DevSecOps de CicloSeguro Lima

## Herramientas y controles de seguridad por fase

| Fase | Herramientas | Control de seguridad integrado (shift-left) |
| --- | --- | --- |
| Plan | Jira: backlog, épicas, sprints y tablero Kanban | Los requisitos de seguridad son historias con criterios Dado/Cuando/Entonces (HU-01 registro seguro, HU-02 ingreso, HU-03 bloqueo, HU-10 moderación) y una tarea de endurecimiento (TR-05). |
| Code | Git y GitHub, ramas `main`, `test` y `feature/*`, plantilla de pull request | Rama `main` protegida con ruleset (pull request obligatorio, checks obligatorios, sin force push). `.gitignore` excluye `.env`. Plantilla de PR con lista de verificación de secretos y pruebas. |
| Build | GitHub Actions, pip, `build.sh` (collectstatic y migrate) | pip-audit y la revisión de dependencias vigilan vulnerabilidades. gitleaks revisa secretos en todo el historial. Se genera un SBOM (CycloneDX) en cada ejecución. |
| Test | `manage.py test` (52 pruebas unitarias y de integración), coverage con mínimo del 80 %, matriz de Python, job con PostgreSQL, flake8 | Pruebas de seguridad: hash PBKDF2, correos y contraseñas inválidos, mensaje de error único, bloqueo tras 5 intentos, escape de HTML, control de acceso, filtros con valores maliciosos. SAST con bandit y CodeQL, escaneo con Trivy y DAST con OWASP ZAP sobre la aplicación desplegada. |
| Release | Pull request de `test` a `main`, commit de fusión, Dependabot | Solo se fusiona con la puerta de calidad en verde (todas las etapas). Dependabot propone actualizaciones de dependencias y de acciones. |
| Deploy | Render, Neon (PostgreSQL con SSL), hook de despliegue desde GitHub Actions | Secretos solo en Render y en los secretos de GitHub. `DEBUG=0`. `check --deploy` sin advertencias en el pipeline. Despliegue solo desde `main` y solo con el pipeline en verde; después se verifican las cabeceras de seguridad en producción. |
| Operate | gunicorn, WhiteNoise, ruta `/salud/` | HTTPS forzado, HSTS, cookies seguras, CSP sin scripts en línea, X-Frame-Options, bloqueo por intentos fallidos (django-axes). |
| Monitor | Registros de Render, health check, pestaña Security de GitHub, alertas de Dependabot | Alertas de CodeQL y de dependencias. Los registros no incluyen contraseñas ni claves. Limitación: no hay APM ni alertas propias. |

## Pipeline unificado (GitHub Actions)

Un solo flujo, `Pipeline DevSecOps` (`.github/workflows/pipeline.yml`), reúne todas las etapas con dependencias explícitas (`needs`). Así cada ejecución muestra en una sola vista el recorrido completo, desde el código hasta la verificación en producción. Se ejecuta en cada pull request y en cada push a `main` y `test`, cada lunes (revisión programada de vulnerabilidades nuevas) y de forma manual.

| Etapa | Trabajo | Qué hace |
| --- | --- | --- |
| 1 Código | Secretos (gitleaks) | Revisa todo el historial de Git en busca de claves y contraseñas. |
| 1 Código | Estilo (flake8) | Verifica el estilo del código y bloquea si hay errores. |
| 1 Código | Revisión de dependencias | En pull requests, informa dependencias nuevas con vulnerabilidades conocidas. |
| 2 Build | Construcción y validación | Instala las dependencias de producción, ejecuta `check`, verifica que no falten migraciones y recopila los estáticos como en producción. Solo corre si la etapa 1 pasó. |
| 3 Test | Pruebas y cobertura | 52 pruebas en Python 3.12 y 3.13 (matriz) con cobertura mínima del 80 % e informe HTML como artefacto. |
| 3 Test | Integración con PostgreSQL | Repite las pruebas en PostgreSQL 16, el mismo motor de producción. |
| 4 Seguridad | SAST con bandit | Análisis estático del código; bloquea con severidad media o alta. |
| 4 Seguridad | SAST con CodeQL | Análisis estático con consultas de seguridad ampliadas; resultados en la pestaña Security. |
| 4 Seguridad | SCA con pip-audit | Vulnerabilidades conocidas en las dependencias de producción. |
| 4 Seguridad | Trivy | Escaneo informativo de dependencias, secretos y configuración. |
| 4 Seguridad | SBOM | Lista de componentes en formato CycloneDX con las versiones instaladas, como artefacto. |
| 4 Seguridad | Configuración de producción | `check --deploy` con `DEBUG=0`. |
| 5 Release | Puerta de calidad | Exige que todas las etapas anteriores hayan pasado y publica una tabla resumen. Es el check obligatorio de `main`. |
| 6 Deploy | Render | Solo en `main`: solicita el despliegue del commit verificado con el hook y espera a que `/salud/` responda. |
| 7 Verificación | Cabeceras en producción | Comprueba HSTS, CSP, X-Frame-Options, nosniff, política de referencia y redirección de HTTP a HTTPS sobre la URL desplegada. |
| 8 DAST | OWASP ZAP | Escaneo dinámico base (baseline) sobre la aplicación desplegada; informe como artefacto. Es informativo y no bloquea. |

Los análisis de Trivy y de ZAP son informativos para no frenar la entrega por hallazgos de bajo riesgo; el resto bloquea la fusión a `main` mediante la puerta de calidad.

## Justificación del stack según el caso

- **Django:** el caso exige cuentas, formularios y catálogos con datos de personas, y Django entrega autenticación, protección CSRF, escape de plantillas y ORM seguros por defecto, lo que permite construir rápido sin descuidar la seguridad.
- **PostgreSQL en Neon:** base relacional con SSL, gratuita y gestionada, adecuada para consultas por distrito y tipo.
- **Render:** despliegue gratuito con HTTPS, variables de entorno y despliegue desde GitHub.
- **GitHub Actions:** integra pruebas, análisis de seguridad y despliegue en el mismo repositorio donde se revisan los cambios.
- **Jira:** backlog, épicas, sprints y tablero que cubren la gestión Scrum pedida.
- **django-axes y CSP:** responden al riesgo principal del caso, que es proteger las cuentas y la información que reporta la comunidad.
