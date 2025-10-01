# 🥊 Modelo de Peleas de Evento
from sqlalchemy import Column, Integer, String, Text, Time, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class PeleaEvento(Base):
    """
    Modelo para peleas que pertenecen a un evento de transmisión.

    Representa cada pelea individual dentro de un evento, con información
    de los gallos participantes (izquierda y derecha del juez), videos,
    resultados y tiempos.
    """
    __tablename__ = "peleas_evento"

    # Identificadores
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(
        Integer,
        ForeignKey("eventos_transmision.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Información de la pelea
    numero_pelea = Column(Integer, nullable=False, comment="Número y orden de la pelea")
    titulo_pelea = Column(String(255), nullable=False)
    descripcion_pelea = Column(Text, nullable=True)

    # 🐔 Gallo IZQUIERDA (del juez)
    galpon_izquierda = Column(String(100), nullable=False, comment="Galpón lado izquierdo")
    gallo_izquierda_nombre = Column(String(100), nullable=False, comment="Gallo lado izquierdo")

    # 🐔 Gallo DERECHA (del juez)
    galpon_derecha = Column(String(100), nullable=False, comment="Galpón lado derecho")
    gallo_derecha_nombre = Column(String(100), nullable=False, comment="Gallo lado derecho")

    # ⏰ Tiempos
    hora_inicio_estimada = Column(Time, nullable=True)
    hora_inicio_real = Column(DateTime, nullable=True, index=True)
    hora_fin_real = Column(DateTime, nullable=True)
    duracion_minutos = Column(Integer, nullable=True)

    # 📊 Resultado
    resultado = Column(
        String(100),
        nullable=True,
        comment="izquierda, derecha, empate, o null"
    )

    # 🎥 Media
    video_url = Column(Text, nullable=True, comment="URL del video en Cloudinary")
    thumbnail_pelea_url = Column(Text, nullable=True)
    estado_video = Column(
        String(50),
        nullable=True,
        default='sin_video',
        index=True,
        comment="sin_video, procesando, disponible"
    )

    # 👤 Auditoría
    admin_editor_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )

    # 🔗 Relaciones
    evento = relationship("EventoTransmision", back_populates="peleas")
    admin_editor = relationship("User", foreign_keys=[admin_editor_id])

    def __repr__(self):
        return f"<PeleaEvento(id={self.id}, evento_id={self.evento_id}, numero={self.numero_pelea}, titulo='{self.titulo_pelea}')>"

    def to_dict(self):
        """Convertir a diccionario para respuestas JSON"""
        return {
            "id": self.id,
            "evento_id": self.evento_id,
            "numero_pelea": self.numero_pelea,
            "titulo_pelea": self.titulo_pelea,
            "descripcion_pelea": self.descripcion_pelea,
            "galpon_izquierda": self.galpon_izquierda,
            "gallo_izquierda_nombre": self.gallo_izquierda_nombre,
            "galpon_derecha": self.galpon_derecha,
            "gallo_derecha_nombre": self.gallo_derecha_nombre,
            "hora_inicio_estimada": self.hora_inicio_estimada.isoformat() if self.hora_inicio_estimada else None,
            "hora_inicio_real": self.hora_inicio_real.isoformat() if self.hora_inicio_real else None,
            "hora_fin_real": self.hora_fin_real.isoformat() if self.hora_fin_real else None,
            "duracion_minutos": self.duracion_minutos,
            "resultado": self.resultado,
            "video_url": self.video_url,
            "thumbnail_pelea_url": self.thumbnail_pelea_url,
            "estado_video": self.estado_video,
            "admin_editor_id": self.admin_editor_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
