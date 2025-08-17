from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base

class PasswordResetToken(Base):
    """Modelo para tokens de recuperación de contraseña"""
    
    __tablename__ = "password_reset_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    token = Column(String(6), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relación con el modelo User
    user = relationship("User", back_populates="password_reset_tokens")
    
    def __repr__(self):
        return f"<PasswordResetToken(email={self.email}, token={self.token}, used={self.used})>"
    
    def is_expired(self):
        """Verificar si el token ha expirado"""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self):
        """Verificar si el token es válido (no usado y no expirado)"""
        return not self.used and not self.is_expired()