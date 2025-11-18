# 💳 Servicio de Mercado Pago - Integración Completa
import os
import logging
import hmac
import hashlib
from typing import Dict, Any, Optional
import mercadopago
from datetime import datetime, timedelta

logger = logging.getLogger("galloapp.mercadopago")

class MercadoPagoService:
    """
    Servicio para integración con Mercado Pago
    
    Funcionalidades:
    - Crear preferencias de pago (checkout)
    - Procesar webhooks
    - Consultar estado de pagos
    - Gestionar suscripciones
    """
    
    def __init__(self):
        """Inicializa el SDK de Mercado Pago"""
        self.access_token = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
        self.public_key = os.getenv("MERCADOPAGO_PUBLIC_KEY")
        self.environment = os.getenv("MERCADOPAGO_ENVIRONMENT", "production")
        self.webhook_url = os.getenv("MERCADOPAGO_WEBHOOK_URL")
        self.webhook_secret = os.getenv("MERCADOPAGO_WEBHOOK_SECRET")
        
        if not self.access_token:
            logger.warning("⚠️ MERCADOPAGO_ACCESS_TOKEN no configurado")
            self.sdk = None
        else:
            self.sdk = mercadopago.SDK(self.access_token)
            logger.info(f"✅ Mercado Pago SDK inicializado - Ambiente: {self.environment}")
            if self.webhook_secret:
                logger.info(f"✅ Webhook Secret configurado para validación de firma")
    
    def crear_preferencia_pago(
        self,
        user_id: int,
        plan_codigo: str,
        plan_nombre: str,
        monto: float,
        user_email: str,
        user_nombre: str = "Usuario"
    ) -> Dict[str, Any]:
        """
        Crea una preferencia de pago en Mercado Pago
        
        Args:
            user_id: ID del usuario
            plan_codigo: Código del plan (basico, premium, profesional)
            plan_nombre: Nombre descriptivo del plan
            monto: Monto a cobrar en soles
            user_email: Email del usuario
            user_nombre: Nombre del usuario
            
        Returns:
            Dict con init_point (URL de pago) y preference_id
        """
        try:
            if not self.sdk:
                raise Exception("Mercado Pago no configurado")
            
            # Construir referencia única
            referencia = f"GALLO_{user_id}_{plan_codigo}_{int(datetime.now().timestamp())}"
            
            # Crear preferencia
            preference_data = {
                "items": [
                    {
                        "title": f"Plan {plan_nombre} - Casta de Gallos",
                        "description": f"Suscripción {plan_nombre} para gestión de gallos de pelea",
                        "quantity": 1,
                        "unit_price": float(monto),
                        "currency_id": "PEN"
                    }
                ],
                "payer": {
                    "name": user_nombre,
                    "email": user_email
                },
                "back_urls": {
                    "success": f"{os.getenv('FRONTEND_URL', 'https://app-gallera-production.up.railway.app')}/pago-exitoso",
                    "failure": f"{os.getenv('FRONTEND_URL', 'https://app-gallera-production.up.railway.app')}/pago-fallido",
                    "pending": f"{os.getenv('FRONTEND_URL', 'https://app-gallera-production.up.railway.app')}/pago-pendiente"
                },
                "auto_return": "approved",
                "notification_url": self.webhook_url,
                "external_reference": referencia,
                "statement_descriptor": "CASTA DE GALLOS",
                "metadata": {
                    "user_id": user_id,
                    "plan_codigo": plan_codigo,
                    "timestamp": datetime.now().isoformat()
                },
                "expires": True,
                "expiration_date_from": datetime.now().isoformat(),
                "expiration_date_to": (datetime.now() + timedelta(hours=24)).isoformat()
            }
            
            # Crear preferencia en Mercado Pago
            preference_response = self.sdk.preference().create(preference_data)
            preference = preference_response["response"]
            
            logger.info(f"✅ Preferencia creada: {preference['id']} para usuario {user_id}")
            
            return {
                "success": True,
                "preference_id": preference["id"],
                "init_point": preference["init_point"],  # URL para web
                "sandbox_init_point": preference.get("sandbox_init_point"),  # URL para testing
                "referencia": referencia,
                "monto": monto,
                "plan_codigo": plan_codigo
            }
            
        except Exception as e:
            logger.error(f"❌ Error creando preferencia de pago: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def obtener_pago(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información de un pago
        
        Args:
            payment_id: ID del pago en Mercado Pago
            
        Returns:
            Dict con información del pago o None si hay error
        """
        try:
            if not self.sdk:
                raise Exception("Mercado Pago no configurado")
            
            payment_response = self.sdk.payment().get(payment_id)
            payment = payment_response["response"]
            
            return {
                "id": payment["id"],
                "status": payment["status"],
                "status_detail": payment["status_detail"],
                "transaction_amount": payment["transaction_amount"],
                "currency_id": payment["currency_id"],
                "payment_method_id": payment["payment_method_id"],
                "payment_type_id": payment["payment_type_id"],
                "date_created": payment["date_created"],
                "date_approved": payment.get("date_approved"),
                "external_reference": payment.get("external_reference"),
                "metadata": payment.get("metadata", {}),
                "payer": {
                    "email": payment["payer"]["email"],
                    "identification": payment["payer"].get("identification", {})
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo pago {payment_id}: {e}")
            return None
    
    def validar_firma_webhook(self, x_signature: str, x_request_id: str, data_id: str) -> bool:
        """
        Valida la firma del webhook de Mercado Pago
        
        Args:
            x_signature: Header x-signature del webhook
            x_request_id: Header x-request-id del webhook
            data_id: ID del recurso notificado
            
        Returns:
            True si la firma es válida, False en caso contrario
        """
        if not self.webhook_secret:
            logger.warning("⚠️ WEBHOOK_SECRET no configurado, saltando validación de firma")
            return True
        
        try:
            # Extraer ts y hash de x-signature
            # Formato: ts=1234567890,v1=hash_value
            parts = {}
            for part in x_signature.split(','):
                key, value = part.split('=')
                parts[key] = value
            
            ts = parts.get('ts')
            received_hash = parts.get('v1')
            
            if not ts or not received_hash:
                logger.error("❌ Firma inválida: falta ts o v1")
                return False
            
            # Crear el manifest (string a firmar)
            manifest = f"id:{data_id};request-id:{x_request_id};ts:{ts};"
            
            # Calcular HMAC SHA256
            calculated_hash = hmac.new(
                self.webhook_secret.encode(),
                manifest.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Comparar hashes
            is_valid = hmac.compare_digest(calculated_hash, received_hash)
            
            if is_valid:
                logger.info("✅ Firma del webhook validada correctamente")
            else:
                logger.error("❌ Firma del webhook inválida")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"❌ Error validando firma del webhook: {e}")
            return False
    
    def procesar_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa notificación webhook de Mercado Pago
        
        Args:
            data: Datos del webhook
            
        Returns:
            Dict con resultado del procesamiento
        """
        try:
            # Extraer información del webhook
            topic = data.get("topic") or data.get("type")
            resource_id = data.get("data", {}).get("id") or data.get("id")
            
            logger.info(f"📬 Webhook recibido - Topic: {topic}, ID: {resource_id}")
            
            if topic == "payment":
                # Obtener información completa del pago
                payment_info = self.obtener_pago(resource_id)
                
                if not payment_info:
                    return {"success": False, "error": "No se pudo obtener información del pago"}
                
                # Extraer metadata
                user_id = payment_info.get("metadata", {}).get("user_id")
                plan_codigo = payment_info.get("metadata", {}).get("plan_codigo")
                
                return {
                    "success": True,
                    "topic": topic,
                    "payment_id": resource_id,
                    "status": payment_info["status"],
                    "status_detail": payment_info["status_detail"],
                    "monto": payment_info["transaction_amount"],
                    "metodo_pago": payment_info["payment_method_id"],
                    "user_id": user_id,
                    "plan_codigo": plan_codigo,
                    "external_reference": payment_info.get("external_reference"),
                    "fecha_aprobacion": payment_info.get("date_approved"),
                    "debe_activar_suscripcion": payment_info["status"] == "approved"
                }
            
            return {
                "success": True,
                "topic": topic,
                "message": f"Topic {topic} no requiere procesamiento"
            }
            
        except Exception as e:
            logger.error(f"❌ Error procesando webhook: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def validar_webhook_signature(self, headers: Dict[str, str], body: str) -> bool:
        """
        Valida la firma del webhook para seguridad
        
        Args:
            headers: Headers HTTP del webhook
            body: Cuerpo del webhook
            
        Returns:
            True si la firma es válida
        """
        # TODO: Implementar validación de firma
        # Mercado Pago envía x-signature y x-request-id
        return True
    
    def procesar_pago_yape(
        self,
        numero_telefono: str,
        otp: str,
        monto: float,
        user_email: str,
        user_id: int,
        plan_codigo: str,
        plan_nombre: str
    ) -> Dict[str, Any]:
        """
        Procesa un pago con Yape usando Mercado Pago API
        
        Args:
            numero_telefono: Número de teléfono de Yape (9 dígitos)
            otp: Código OTP de Yape
            monto: Monto a cobrar
            user_email: Email del usuario
            user_id: ID del usuario
            plan_codigo: Código del plan
            plan_nombre: Nombre del plan
            
        Returns:
            Dict con resultado del pago
        """
        try:
            if not self.sdk:
                raise Exception("Mercado Pago no configurado")
            
            logger.info(f"📱 Procesando pago con Yape - Usuario: {user_id}, Monto: S/. {monto}")
            
            # Construir referencia única
            referencia = f"YAPE_{user_id}_{plan_codigo}_{int(datetime.now().timestamp())}"
            
            # Crear el pago con Yape
            payment_data = {
                "transaction_amount": float(monto),
                "description": f"Plan {plan_nombre} - Casta de Gallos",
                "payment_method_id": "yape",
                "payer": {
                    "email": user_email,
                    "identification": {
                        "type": "DNI",
                        "number": numero_telefono  # Usamos el número como identificación
                    }
                },
                "token": otp,  # El OTP actúa como token
                "installments": 1,
                "external_reference": referencia,
                "notification_url": self.webhook_url,
                "metadata": {
                    "user_id": user_id,
                    "plan_codigo": plan_codigo,
                    "numero_telefono": numero_telefono,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            # Crear el pago
            logger.info(f"📤 Enviando pago a Mercado Pago: {payment_data}")
            payment_response = self.sdk.payment().create(payment_data)
            logger.info(f"📥 Respuesta de Mercado Pago: {payment_response}")
            
            # Manejar diferentes formatos de respuesta del SDK
            if isinstance(payment_response, dict):
                payment = payment_response.get("response", payment_response)
            else:
                payment = payment_response
            
            logger.info(f"✅ Pago procesado - ID: {payment.get('id')}, Estado: {payment.get('status')}")
            
            return {
                "success": True,
                "payment_id": str(payment.get("id", "")),
                "status": payment.get("status", "pending"),
                "status_detail": payment.get("status_detail", ""),
                "monto": payment.get("transaction_amount", monto),
                "metodo_pago": "yape",
                "fecha_creacion": payment.get("date_created", datetime.now().isoformat()),
                "fecha_aprobacion": payment.get("date_approved"),
                "external_reference": referencia
            }
            
        except Exception as e:
            logger.error(f"❌ Error procesando pago con Yape: {e}")
            error_msg = str(e)
            
            # Extraer mensaje de error más específico si está disponible
            if hasattr(e, 'response') and hasattr(e.response, 'json'):
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('message', error_msg)
                except:
                    pass
            
            return {
                "success": False,
                "error": error_msg
            }
    
    def obtener_metodos_pago_disponibles(self) -> Dict[str, Any]:
        """
        Obtiene métodos de pago disponibles en Perú
        
        Returns:
            Dict con métodos de pago disponibles
        """
        try:
            if not self.sdk:
                raise Exception("Mercado Pago no configurado")
            
            payment_methods = self.sdk.payment_methods().list_all()
            
            return {
                "success": True,
                "metodos": payment_methods["response"]
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo métodos de pago: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Instancia global del servicio
mercadopago_service = MercadoPagoService()
