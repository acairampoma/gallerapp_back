# 🔔 MODELO FCM TOKEN - FIREBASE CLOUD MESSAGING
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class FCMToken(Base):
    """Modelo para almacenar tokens FCM de usuarios"""
    __tablename__ = "fcm_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    fcm_token = Column(String(255), nullable=False, unique=True, index=True)
    platform = Column(String(20), nullable=False)  # android, ios, web
    device_info = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relación con usuarios
    user = relationship("User")  # back_populates removido temporalmente
    
    def __repr__(self):
        return f"<FCMToken(user_id={self.user_id}, platform={self.platform}, active={self.is_active})>"