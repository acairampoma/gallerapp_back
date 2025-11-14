#!/usr/bin/env python3
"""
Script para crear tablas de usuarios y perfiles en PostgreSQL
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine
from app.models.user import User
from app.models.profile import Profile
from app.core.security import SecurityService

def create_tables():
    """Crear tablas en la base de datos"""
    print("🗄️ Creando tablas en PostgreSQL...")
    
    # Crear tablas
    User.metadata.create_all(bind=engine)
    Profile.metadata.create_all(bind=engine)
    
    print("✅ Tablas creadas exitosamente!")
    print("📋 Tablas: users, profiles")

def create_test_users():
    """Crear usuarios de prueba Juan y Alan"""
    from app.database import SessionLocal
    from app.schemas.auth import UserRegister
    from app.services.auth_service import AuthService
    
    db = SessionLocal()
    
    try:
        print("👥 Creando usuarios de prueba...")
        
        # Usuario 1: Juan Salas Carrillo
        juan_data = UserRegister(
            email="juan.salas@galloapp.com",
            password="123456",
            nombre_completo="Juan Salas Carrillo",
            telefono="987654321",
            nombre_galpon="Gallo de Oro",
            ciudad="Lima",
            ubigeo="150101"
        )
        
        # Usuario 2: Alan Isaias Cairampoma Carrillo  
        alan_data = UserRegister(
            email="alan.cairampoma@galloapp.com",
            password="123456",
            nombre_completo="Alan Isaias Cairampoma Carrillo",
            telefono="987654322",
            nombre_galpon="Gallera Collicana", 
            ciudad="Lima",
            ubigeo="150101"
        )
        
        # Registrar usuarios
        try:
            juan_user = AuthService.register_user(db, juan_data)
            print(f"✅ Usuario creado: {juan_user.email}")
        except Exception as e:
            print(f"⚠️ Juan ya existe: {e}")
        
        try:
            alan_user = AuthService.register_user(db, alan_data)
            print(f"✅ Usuario creado: {alan_user.email}")
        except Exception as e:
            print(f"⚠️ Alan ya existe: {e}")
            
        print("🎯 Usuarios de prueba listos!")
        print("📧 Emails: juan.salas@galloapp.com / alan.cairampoma@galloapp.com")
        print("🔑 Password: 123456")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🐓 Inicializando base de datos GalloApp...")
    
    # Crear tablas
    create_tables()
    
    # Crear usuarios de prueba
    create_test_users()
    
    print("🚀 Base de datos lista para usar!")
