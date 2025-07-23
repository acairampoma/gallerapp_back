#!/usr/bin/env python3
"""
Script para actualizar passwords de Juan y Alan con hash correcto
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.user import User
from app.core.security import SecurityService

def update_passwords():
    """Actualizar passwords con hash correcto para 123456"""
    db = SessionLocal()
    
    try:
        print("🔐 Actualizando passwords...")
        
        # Generar hash correcto para "123456"
        correct_hash = SecurityService.get_password_hash("123456")
        print(f"✅ Hash generado: {correct_hash}")
        
        # Actualizar Juan
        juan = db.query(User).filter(User.email == "juan.salas@galloapp.com").first()
        if juan:
            juan.password_hash = correct_hash
            print(f"✅ Password actualizado para: {juan.email}")
        else:
            print("⚠️ Juan no encontrado")
        
        # Actualizar Alan
        alan = db.query(User).filter(User.email == "alan.cairampoma@galloapp.com").first()
        if alan:
            alan.password_hash = correct_hash
            print(f"✅ Password actualizado para: {alan.email}")
        else:
            print("⚠️ Alan no encontrado")
        
        # Commit cambios
        db.commit()
        print("💾 Cambios guardados en base de datos")
        
        print("\n🎯 PASSWORDS ACTUALIZADOS:")
        print("📧 Email: juan.salas@galloapp.com")
        print("📧 Email: alan.cairampoma@galloapp.com") 
        print("🔑 Password: 123456")
        print("\n✅ Ahora puedes hacer login con estos usuarios!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🔐 Actualizando passwords de Juan y Alan...")
    update_passwords()
    print("🚀 Script completado!")
