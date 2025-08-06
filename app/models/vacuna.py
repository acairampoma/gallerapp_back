from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Vacuna(Base):
    __tablename__ = "vacunas"
    
    id = Column(Integer, primary_key=True, index=True)
    gallo_id = Column(Integer, ForeignKey("gallos.id", ondelete="CASCADE"), nullable=True)
    tipo_vacuna = Column(String(255), nullable=False)
    laboratorio = Column(String(255), nullable=True)
    fecha_aplicacion = Column(Date, nullable=False)
    proxima_dosis = Column(Date, nullable=True)
    veterinario_nombre = Column(String(255), nullable=True)
    clinica = Column(String(255), nullable=True)
    dosis = Column(String(50), nullable=True)
    notas = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relación con gallos (asumiendo que existe el modelo Gallo)
    # gallo = relationship("Gallo", back_populates="vacunas")