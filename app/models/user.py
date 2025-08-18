from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    """Modelo de Usuario (Solo autenticación)"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    last_login = Column(DateTime)
    refresh_token = Column(String(500))
    
    # Campos para admin
    es_admin = Column(Boolean, default=False)
    recibe_notificaciones_admin = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones
    suscripciones = relationship("Suscripcion", back_populates="user")
    inversiones = relationship("Inversion", back_populates="user")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user")
    fcm_tokens = relationship("FCMToken", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"
