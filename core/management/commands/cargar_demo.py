"""Carga datos ficticios de demostración (rutas, incidentes y estacionamientos). Es idempotente."""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from estacionamientos.models import Estacionamiento
from incidentes.models import Incidente
from rutas.models import Ruta

RUTAS = [
    ("Malecón de Miraflores a Barranco", "miraflores", "barranco", 4.2, "segregada",
     "Tramo costero con ciclovía exclusiva y buena iluminación."),
    ("Corredor San Isidro a Magdalena", "san_isidro", "magdalena", 5.1, "parcial",
     "Ciclovía con cruces compartidos con vehículos en dos intersecciones."),
    ("Surco a Surquillo por avenida principal", "surco", "surquillo", 6.3, "parcial",
     "Tramos en buen estado, con invasión ocasional de vehículos estacionados."),
    ("Lince a Jesús María", "lince", "jesus_maria", 2.8, "segregada",
     "Ciclovía corta y continua entre parques."),
    ("San Borja a La Molina", "san_borja", "la_molina", 7.5, "sin_ciclovia",
     "Sin ciclovía en la mitad del recorrido; se recomienda precaución."),
    ("Cercado de Lima a San Miguel", "lima", "san_miguel", 8.0, "parcial",
     "Conecta con la costa; varios tramos en mal estado."),
]

INCIDENTES = [
    ("robo", "miraflores", "Intento de robo de bicicleta cerca del malecón (dato ficticio).", 5),
    ("robo", "lima", "Robo de accesorios en un cruce concurrido (dato ficticio).", 12),
    ("accidente", "san_isidro", "Choque leve en un cruce sin señalización (dato ficticio).", 20),
    ("via_mal_estado", "surco", "Baches profundos en el carril de bicicletas (dato ficticio).", 9),
    ("invasion", "lince", "Vehículos estacionados sobre la ciclovía (dato ficticio).", 3),
    ("accidente", "lima", "Caída por pista resbalosa en hora punta (dato ficticio).", 15),
    ("robo", "san_miguel", "Robo de bicicleta sin candado en vía pública (dato ficticio).", 30),
    ("via_mal_estado", "san_borja", "Tramo sin pavimentar que obliga a usar la pista (dato ficticio).", 7),
]

ESTACIONAMIENTOS = [
    ("Bicicletero municipal del parque", "miraflores", "Parque central", "publico_vigilado", 40, True, True),
    ("Centro comercial: zona de bicicletas", "san_isidro", "Zona financiera", "centro_comercial", 25, True, True),
    ("Estación de bicicletas del corredor", "surco", "Av. principal, cuadra 10", "publico_vigilado", 30, False, True),
    ("Bicicletero universitario", "san_miguel", "Campus universitario", "privado", 60, True, True),
    ("Bicicletero de la plaza", "lima", "Plaza central", "publico_vigilado", 20, True, False),
]


class Command(BaseCommand):
    help = "Carga datos ficticios de demostración."

    def handle(self, *args, **opciones):
        for nombre, origen, destino, km, estado, descripcion in RUTAS:
            Ruta.objects.get_or_create(
                nombre=nombre,
                defaults={"distrito_origen": origen, "distrito_destino": destino, "longitud_km": km,
                          "estado_ciclovia": estado, "descripcion": descripcion},
            )
        for tipo, distrito, descripcion, dias in INCIDENTES:
            Incidente.objects.get_or_create(
                descripcion=descripcion,
                defaults={"tipo": tipo, "distrito": distrito, "fecha_hecho": timezone.localdate() - timedelta(days=dias)},
            )
        for nombre, distrito, direccion, tipo, capacidad, vigilancia, gratis in ESTACIONAMIENTOS:
            Estacionamiento.objects.get_or_create(
                nombre=nombre,
                defaults={"distrito": distrito, "direccion": direccion, "tipo": tipo, "capacidad": capacidad,
                          "vigilancia_24h": vigilancia, "gratuito": gratis, "aprobado": True},
            )
        self.stdout.write("Datos de demostración cargados.")
