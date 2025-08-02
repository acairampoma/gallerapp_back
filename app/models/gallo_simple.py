# 🔥 app/models/gallo_simple.py - Modelo ÉPICO con Técnica Recursiva Genealógica
from sqlalchemy import Column, Integer, String, Date, Numeric, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Gallo(Base):
    __tablename__ = "gallos"
    
    # ========================
    # 🎯 CAMPOS BÁSICOS
    # ========================
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    raza_id = Column(String(100), nullable=True)  # Cambiado de FK a varchar
    
    # ========================
    # 🐓 INFORMACIÓN DEL GALLO
    # ========================
    nombre = Column(String(255), nullable=False)
    codigo_identificacion = Column(String(50), nullable=False, index=True)
    fecha_nacimiento = Column(Date, nullable=True)
    peso = Column(Numeric(5, 2), nullable=True)  # kg
    altura = Column(Integer, nullable=True)  # cm
    color = Column(String(100), nullable=True)  # Color principal
    estado = Column(String(20), default="activo")  # activo, inactivo, padre, madre, campeon, retirado
    procedencia = Column(String(255), nullable=True)
    notas = Column(Text, nullable=True)
    
    # ========================
    # 🧬 TÉCNICA RECURSIVA GENEALÓGICA (CAMPOS ÉPICOS)
    # ========================
    id_gallo_genealogico = Column(Integer, nullable=True, index=True)  # 🔥 CAMPO MÁGICO - Vincula familias
    padre_id = Column(Integer, ForeignKey("gallos.id"), nullable=True, index=True)
    madre_id = Column(Integer, ForeignKey("gallos.id"), nullable=True, index=True)
    tipo_registro = Column(String(20), default="principal")  # principal, padre_generado, madre_generada
    
    # ========================
    # 📸 GESTIÓN DE FOTOS (CLOUDINARY)
    # ========================
    foto_principal_url = Column(Text, nullable=True)  # URL original
    url_foto_cloudinary = Column(Text, nullable=True)  # URL optimizada Cloudinary
    fotos_adicionales = Column(JSON, nullable=True)  # Array de URLs adicionales
    
    # ========================
    # 📋 CAMPOS ADICIONALES DETALLADOS
    # ========================
    color_plumaje = Column(String(100), nullable=True)  # Detalle específico del plumaje
    color_placa = Column(String(50), nullable=True)  # Color de la placa identificatoria
    ubicacion_placa = Column(String(50), nullable=True)  # Pata Derecha, Pata Izquierda, Ambas Patas
    color_patas = Column(String(50), nullable=True)  # Color de las patas
    criador = Column(String(255), nullable=True)  # Nombre del criador original
    propietario_actual = Column(String(255), nullable=True)  # Propietario actual
    observaciones = Column(Text, nullable=True)  # Observaciones adicionales
    numero_registro = Column(String(100), nullable=True)  # Número de registro específico
    
    # ========================
    # ⏰ TIMESTAMPS
    # ========================
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # ========================
    # 🔗 RELACIONES SQLALCHEMY
    # ========================
    # Relación con raza removida - ahora raza_id es varchar libre
    
    # 🧬 Relaciones genealógicas (auto-referencia)
    padre = relationship(
        "Gallo", 
        remote_side=[id], 
        foreign_keys=[padre_id],
        post_update=True,  # Evita problemas de dependencias circulares
        back_populates="hijos_como_padre"
    )
    
    madre = relationship(
        "Gallo", 
        remote_side=[id], 
        foreign_keys=[madre_id],
        post_update=True,  # Evita problemas de dependencias circulares
        back_populates="hijos_como_madre"
    )
    
    # 👶 Relaciones inversas (hijos)
    hijos_como_padre = relationship(
        "Gallo",
        foreign_keys=[padre_id],
        back_populates="padre",
        overlaps="padre"
    )
    
    hijos_como_madre = relationship(
        "Gallo",
        foreign_keys=[madre_id], 
        back_populates="madre",
        overlaps="madre"
    )
    
    # ========================
    # 🛠️ MÉTODOS HELPER ÉPICOS
    # ========================
    
    def get_familia_completa(self, session):
        """🔥 Obtener toda la familia por id_gallo_genealogico"""
        if not self.id_gallo_genealogico:
            return [self]
        
        return session.query(Gallo).filter(
            Gallo.id_gallo_genealogico == self.id_gallo_genealogico
        ).all()
    
    def get_ancestros(self, session, max_depth=5):
        """🌳 Obtener árbol genealógico hacia arriba (ancestros)"""
        ancestros = []
        nivel = 0
        
        def obtener_padres_recursivo(gallo, nivel_actual):
            if nivel_actual >= max_depth:
                return
            
            if gallo.padre:
                ancestros.append({
                    'gallo': gallo.padre,
                    'relacion': 'padre',
                    'nivel': nivel_actual + 1
                })
                obtener_padres_recursivo(gallo.padre, nivel_actual + 1)
            
            if gallo.madre:
                ancestros.append({
                    'gallo': gallo.madre,
                    'relacion': 'madre', 
                    'nivel': nivel_actual + 1
                })
                obtener_padres_recursivo(gallo.madre, nivel_actual + 1)
        
        obtener_padres_recursivo(self, nivel)
        return ancestros
    
    def get_descendientes(self, session):
        """👶 Obtener todos los descendientes (hijos)"""
        descendientes = []
        
        # Hijos donde este gallo es padre
        hijos_padre = session.query(Gallo).filter(Gallo.padre_id == self.id).all()
        for hijo in hijos_padre:
            descendientes.append({
                'gallo': hijo,
                'relacion': 'hijo_como_padre'
            })
        
        # Hijos donde este gallo es madre
        hijos_madre = session.query(Gallo).filter(Gallo.madre_id == self.id).all()
        for hijo in hijos_madre:
            descendientes.append({
                'gallo': hijo,
                'relacion': 'hijo_como_madre'
            })
        
        return descendientes
    
    def __repr__(self):
        return f"<Gallo(id={self.id}, nombre='{self.nombre}', codigo='{self.codigo_identificacion}', genealogico={self.id_gallo_genealogico})>"
