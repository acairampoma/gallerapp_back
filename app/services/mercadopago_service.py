# 💳 Servicio de Mercado Pago - Integración Completa
import os
import logging
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
        
        if not self.access_token:
            logger.warning("⚠️ MERCADOPAGO_ACCESS_TOKEN no configurado")
            self.sdk = None
        else:
            self.sdk = mercadopago.SDK(self.access_token)
            logger.info(f"✅ Mercado Pago SDK inicializado - Ambiente: {self.environment}")
    
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
