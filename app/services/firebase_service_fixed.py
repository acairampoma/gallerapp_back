# 🔥 FIREBASE SERVICE - MEJORES PRÁCTICAS OFICIALES PYTHON
# Archivo: app/services/firebase_service_fixed.py

import os
import json
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from firebase_admin import credentials, messaging, initialize_app, get_app
import firebase_admin
from pydantic import BaseModel
import asyncio
from functools import wraps

# Configurar logging
logger = logging.getLogger(__name__)

class FirebaseError(Exception):
    """Excepción personalizada para errores de Firebase"""
    pass

class NotificationResult(BaseModel):
    """Modelo para resultado de notificación"""
    success: bool
    success_count: int = 0
    failure_count: int = 0
    message_id: Optional[str] = None
    failed_tokens: List[Dict[str, str]] = []
    error: Optional[str] = None

def handle_firebase_errors(func):
    """Decorador para manejar errores de Firebase"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except messaging.FirebaseError as e:
            logger.error(f"❌ Firebase Error: {e}")
            return NotificationResult(
                success=False,
                error=f"Firebase Error: {e.code} - {e.description}"
            )
        except Exception as e:
            logger.error(f"❌ Unexpected Error: {e}")
            return NotificationResult(
                success=False,
                error=f"Unexpected Error: {str(e)}"
            )
    return wrapper

class FirebaseService:
    """
    Servicio Firebase siguiendo mejores prácticas oficiales de Google
    Documentación: https://firebase.google.com/docs/admin/setup
    """
    
    # Singleton pattern
    _instance: Optional['FirebaseService'] = None
    _is_initialized: bool = False
    _app: Optional[firebase_admin.App] = None
    
    def __new__(cls) -> 'FirebaseService':
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializar servicio con lazy loading"""
        if not self._is_