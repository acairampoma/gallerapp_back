# 💰 Modelo de Inversiones
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.database import Base

class TipoGastoEnum(enum.Enum):
    ALIMENTO = "alimento"
    MEDICINA = "medicina"
    LIMPIEZA_GALPON = "limpieza_galpon"
    ENTRENADOR = "entrenador"

class Inversion(Base):
    __tablename__ = "inversiones"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    año = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    tipo_gasto = Column(Enum(TipoGastoEnum), nullable=False)
    costo = Column(Numeric(10, 2), nullable=False, default=0.00)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    user = relationship("User", back_populates="inversiones")