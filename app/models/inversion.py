# 💰 Modelo de Inversiones
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base

class Inversion(Base):
    __tablename__ = "inversiones"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    año = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    tipo_gasto = Column(String(50), nullable=False)  # String directo, BD maneja el ENUM
    costo = Column(Numeric(10, 2), nullable=False, default=0.00)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    user = relationship("User", back_populates="inversiones")