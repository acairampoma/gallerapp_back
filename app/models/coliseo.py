from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, func
from sqlalchemy.orm import relationship
from app.database import Base

class Coliseo(Base):
    """Modelo de Coliseo para transmisiones"""
    __tablename__ = "coliseos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    direccion = Column(Text)
    ciudad = Column(String(100), nullable=False)
    departamento = Column(String(100))
    aforo_maximo = Column(Integer)
    descripcion = Column(Text)
    imagen_url = Column(Text)
    telefono = Column(String(20))
    email = Column(String(255))
    tipo_coliseo = Column(String(50), default='local')  # local, grande, especial
    activo = Column(Boolean, default=True)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relaciones
    eventos = relationship("EventoTransmision", back_populates="coliseo")

    def __repr__(self):
        return f"<Coliseo(id={self.id}, nombre='{self.nombre}', ciudad='{self.ciudad}')>"