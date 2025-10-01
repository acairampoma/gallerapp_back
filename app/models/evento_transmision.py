from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class EventoTransmision(Base):
    """Modelo de Evento de Transmisión"""
    __tablename__ = "eventos_transmision"

    id = Column(Integer, primary_key=True, index=True)
    coliseo_id = Column(Integer, ForeignKey("coliseos.id"))
    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text)
    fecha_evento = Column(DateTime, nullable=False)
    fecha_fin_evento = Column(DateTime)
    url_transmision = Column(Text, nullable=False)  # URL de Kick.com
    estado = Column(String(50), default='programado')  # programado, en_vivo, finalizado, cancelado
    tipo_evento = Column(String(100), default='local')  # local, grande, especial
    precio_entrada = Column(Numeric(10, 2))
    es_premium = Column(Boolean, default=False)
    thumbnail_url = Column(Text)
    admin_creador_id = Column(Integer, ForeignKey("users.id"))

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relaciones
    coliseo = relationship("Coliseo", back_populates="eventos")
    admin_creador = relationship("User")
    peleas = relationship("PeleaEvento", back_populates="evento", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<EventoTransmision(id={self.id}, titulo='{self.titulo}', estado='{self.estado}')>"