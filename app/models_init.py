# 🗄️ app/models_init.py - Importar modelos en orden correcto para SQLAlchemy
"""
Este archivo importa todos los modelos en el orden correcto para evitar
errores de dependencias circulares y relaciones.
"""

# Importar Base primero
from app.database import Base

# Importar modelos básicos sin dependencias
from app.models.user import User
from app.models.raza_simple import Raza
from app.models.fcm_token import FCMToken
from app.models.coliseo import Coliseo

# Importar modelos que dependen de otros (después)
from app.models.profile import Profile
from app.models.gallo_simple import Gallo
# from app.models.vacuna import Vacuna  # TEMPORALMENTE COMENTADO
from app.models.pelea import Pelea
from app.models.tope import Tope
from app.models.evento_transmision import EventoTransmision
from app.models.pelea_evento import PeleaEvento

# Lista de todos los modelos disponibles
__all__ = [
    "Base",
    "User",
    "Profile",
    "Raza",
    "Gallo",
    "FCMToken",
    # "Vacuna"  # TEMPORALMENTE COMENTADO
    "Pelea",
    "Tope",
    "Coliseo",
    "EventoTransmision",
    "PeleaEvento"
]

def create_all_tables(engine):
    """Crear todas las tablas en el orden correcto"""
    Base.metadata.create_all(bind=engine)
    print("✅ Todas las tablas creadas exitosamente")

def get_all_models():
    """Obtener lista de todos los modelos"""
    return {
        'User': User,
        'Profile': Profile,
        'Raza': Raza,
        'Gallo': Gallo,
        'FCMToken': FCMToken,
        # 'Vacuna': Vacuna  # TEMPORALMENTE COMENTADO
        'Pelea': Pelea,
        'Tope': Tope,
        'Coliseo': Coliseo,
        'EventoTransmision': EventoTransmision,
        'PeleaEvento': PeleaEvento
    }
