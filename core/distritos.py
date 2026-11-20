"""Distritos de Lima usados como catálogo común de rutas, incidentes y estacionamientos."""

DISTRITOS = [
    ("barranco", "Barranco"),
    ("chorrillos", "Chorrillos"),
    ("jesus_maria", "Jesús María"),
    ("la_molina", "La Molina"),
    ("lima", "Lima (Cercado)"),
    ("lince", "Lince"),
    ("magdalena", "Magdalena del Mar"),
    ("miraflores", "Miraflores"),
    ("san_borja", "San Borja"),
    ("san_isidro", "San Isidro"),
    ("san_miguel", "San Miguel"),
    ("surco", "Santiago de Surco"),
    ("surquillo", "Surquillo"),
]

CLAVES_DISTRITO = {clave for clave, _ in DISTRITOS}


def distrito_valido(valor):
    """Devuelve el valor si es un distrito del catálogo; si no, cadena vacía."""
    return valor if valor in CLAVES_DISTRITO else ""
