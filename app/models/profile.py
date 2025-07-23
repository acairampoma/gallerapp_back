from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Date, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Profile(Base):
    """Modelo de Perfil (Datos personales separados)"""
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    nombre_completo = Column(String(255), nullable=False)
    telefono = Column(String(20))
    nombre_galpon = Column(String(255))
    direccion = Column(Text)
    ciudad = Column(String(100))
    ubigeo = Column(String(10))  # Código ubigeo Lima: 150101
    pais = Column(String(100), default="Perú")
    avatar_url = Column(Text)  # URL Cloudinary
    fecha_nacimiento = Column(Date)
    biografia = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relación con User
    user = relationship("User", backref="profile")

    def __repr__(self):
        return f"<Profile(id={self.id}, nombre='{self.nombre_completo}')>"
