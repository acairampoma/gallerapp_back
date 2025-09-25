# 🛒 Modelos de Marketplace - Sistema de Publicaciones
from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime


class MarketplacePublicacion(Base):
    """Publicaciones de gallos en el marketplace"""
    __tablename__ = "marketplace_publicaciones"

    # Campos principales
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # Usuario que publica
    gallo_id = Column(Integer, ForeignKey("gallos.id"), nullable=False, index=True)  # Gallo publicado
    precio = Column(DECIMAL(10, 2), nullable=False)
    estado = Column(String(50), default="venta", nullable=False, index=True)  # 'venta', 'vendido', 'pausado'
    fecha_publicacion = Column(DateTime, default=func.now(), nullable=False, index=True)
    icono_ejemplo = Column(String(100), default="🐓", nullable=True)  # Ícono visual

    # Campos de auditoría
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # Usuario que creó
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # Usuario que actualizó

    # Relaciones (definir cuando estén los modelos correspondientes)
    # user = relationship("User", foreign_keys=[user_id], back_populates="marketplace_publicaciones")
    # gallo = relationship("Gallo", back_populates="marketplace_publicacion")
    # creator = relationship("User", foreign_keys=[created_by])
    # updater = relationship("User", foreign_keys=[updated_by])

    def __repr__(self):
        return f"<MarketplacePublicacion(id={self.id}, gallo_id={self.gallo_id}, precio={self.precio}, estado='{self.estado}')>"

    @property
    def esta_disponible(self):
        """Verifica si la publicación está disponible para compra"""
        return self.estado == "venta"

    @property
    def esta_vendido(self):
        """Verifica si la publicación ya fue vendida"""
        return self.estado == "vendido"

    @property
    def esta_pausado(self):
        """Verifica si la publicación está pausada"""
        return self.estado == "pausado"

    def to_dict(self):
        """Convierte el modelo a diccionario para API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'gallo_id': self.gallo_id,
            'precio': float(self.precio),
            'estado': self.estado,
            'fecha_publicacion': self.fecha_publicacion.isoformat() if self.fecha_publicacion else None,
            'icono_ejemplo': self.icono_ejemplo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
        }


class MarketplaceFavorito(Base):
    """Favoritos de usuarios en el marketplace"""
    __tablename__ = "marketplace_favoritos"

    # Campos principales
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # Usuario que marca favorito
    publicacion_id = Column(Integer, ForeignKey("marketplace_publicaciones.id"), nullable=False, index=True)  # Publicación favorita
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relaciones (definir cuando estén los modelos correspondientes)
    # user = relationship("User", back_populates="marketplace_favoritos")
    # publicacion = relationship("MarketplacePublicacion", back_populates="favoritos")

    def __repr__(self):
        return f"<MarketplaceFavorito(id={self.id}, user_id={self.user_id}, publicacion_id={self.publicacion_id})>"

    def to_dict(self):
        """Convierte el modelo a diccionario para API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'publicacion_id': self.publicacion_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }