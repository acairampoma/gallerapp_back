# 📱 Servicio de Generación QR Yape - Sistema de Pagos
import qrcode
import io
import base64
from typing import Optional, Dict, Tuple
from decimal import Decimal
import logging
import hashlib
from datetime import datetime, timedelta
import cloudinary.uploader
from PIL import Image, ImageDraw, ImageFont
import os

logger = logging.getLogger(__name__)

class QRYapeService:
    """Servicio para generar códigos QR para pagos Yape"""
    
    # Configuración Yape (datos ficticios para demo)
    YAPE_MERCHANT_ID = "GALLOAPP2025"
    YAPE_MERCHANT_NAME = "Gallo App Premium"
    YAPE_PHONE = "999888777"  # Número Yape del negocio
    
    def __init__(self):
        self.qr_version = 1
        self.qr_error_correction = qrcode.constants.ERROR_CORRECT_M
        self.qr_box_size = 10
        self.qr_border = 4
    
    def generar_qr_yape(
        self, 
        monto: Decimal, 
        referencia: str,
        concepto: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Genera un código QR para pago con Yape
        
        Returns:
            Tuple[qr_data, qr_base64]: Los datos del QR y la imagen en base64
        """
        try:
            # Generar datos del QR según protocolo Yape
            qr_data = self._construir_datos_yape(monto, referencia, concepto)
            
            # Crear el código QR
            qr = qrcode.QRCode(
                version=self.qr_version,
                error_correction=self.qr_error_correction,
                box_size=self.qr_box_size,
                border=self.qr_border,
            )
            
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            # Generar imagen QR personalizada
            qr_image = self._crear_imagen_personalizada(qr, monto)
            
            # Convertir a base64
            buffer = io.BytesIO()
            qr_image.save(buffer, format='PNG', quality=95)
            qr_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            logger.info(f"QR generado exitosamente para monto {monto}, ref: {referencia}")
            return qr_data, qr_base64
            
        except Exception as e:
            logger.error(f"Error generando QR Yape: {e}")
            raise ValueError(f"No se pudo generar el código QR: {e}")
    
    def _construir_datos_yape(
        self, 
        monto: Decimal, 
        referencia: str,
        concepto: Optional[str] = None
    ) -> str:
        """Construye la cadena de datos para el QR Yape"""
        
        # Formato simplificado para demo (en producción usar protocolo oficial Yape)
        concepto_final = concepto or f"Plan Premium - {referencia}"
        
        qr_data = (
            f"yape://"
            f"merchant={self.YAPE_MERCHANT_ID}&"
            f"phone={self.YAPE_PHONE}&"
            f"amount={monto}&"
            f"currency=PEN&"
            f"reference={referencia}&"
            f"concept={concepto_final}&"
            f"timestamp={int(datetime.now().timestamp())}"
        )
        
        return qr_data
    
    def _crear_imagen_personalizada(self, qr: qrcode.QRCode, monto: Decimal) -> Image.Image:
        """Crea una imagen QR personalizada con branding"""
        
        # Generar imagen QR base
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Crear imagen más grande para agregar elementos
        width, height = qr_img.size
        new_height = height + 120  # Espacio para header y footer
        new_width = width + 40
        
        # Crear imagen final
        final_img = Image.new('RGB', (new_width, new_height), 'white')
        
        # Pegar QR en el centro
        qr_x = (new_width - width) // 2
        qr_y = 80
        final_img.paste(qr_img, (qr_x, qr_y))
        
        # Agregar texto (header y footer)
        draw = ImageDraw.Draw(final_img)
        
        try:
            # Usar fuente del sistema si está disponible
            font_title = ImageFont.truetype("arial.ttf", 16)
            font_info = ImageFont.truetype("arial.ttf", 12)
        except:
            # Fallback a fuente por defecto
            font_title = ImageFont.load_default()
            font_info = ImageFont.load_default()
        
        # Header
        header_text = "🐓 Gallo App - Pago con Yape"
        bbox = draw.textbbox((0, 0), header_text, font=font_title)
        text_width = bbox[2] - bbox[0]
        text_x = (new_width - text_width) // 2
        draw.text((text_x, 20), header_text, fill="black", font=font_title)
        
        # Monto
        monto_text = f"Monto: S/. {monto}"
        bbox = draw.textbbox((0, 0), monto_text, font=font_info)
        text_width = bbox[2] - bbox[0]
        text_x = (new_width - text_width) // 2
        draw.text((text_x, 45), monto_text, fill="green", font=font_info)
        
        # Footer
        footer_text = "Escanea con tu app Yape"
        bbox = draw.textbbox((0, 0), footer_text, font=font_info)
        text_width = bbox[2] - bbox[0]
        text_x = (new_width - text_width) // 2
        draw.text((text_x, new_height - 30), footer_text, fill="gray", font=font_info)
        
        return final_img
    
    async def subir_qr_cloudinary(
        self, 
        qr_base64: str, 
        referencia: str,
        user_id: int
    ) -> str:
        """Sube el QR a Cloudinary y retorna la URL"""
        try:
            # Decodificar base64
            qr_bytes = base64.b64decode(qr_base64)
            
            # Subir a Cloudinary
            upload_result = cloudinary.uploader.upload(
                qr_bytes,
                folder=f"galloapp/pagos/qr/user_{user_id}",
                public_id=f"qr_yape_{referencia}_{int(datetime.now().timestamp())}",
                resource_type="image",
                format="png",
                quality="auto",
                tags=["qr", "yape", "pago", f"user_{user_id}"]
            )
            
            url = upload_result.get('secure_url')
            logger.info(f"QR subido a Cloudinary: {url}")
            return url
            
        except Exception as e:
            logger.error(f"Error subiendo QR a Cloudinary: {e}")
            # Retornar URL de fallback o lanzar excepción según preferencia
            raise ValueError(f"No se pudo subir el QR: {e}")
    
    def generar_referencia_pago(self, user_id: int, plan_codigo: str) -> str:
        """Genera una referencia única para el pago"""
        timestamp = int(datetime.now().timestamp())
        data = f"{user_id}_{plan_codigo}_{timestamp}"
        hash_obj = hashlib.md5(data.encode())
        return f"GP{hash_obj.hexdigest()[:8].upper()}"
    
    def validar_qr_vigente(self, created_at: datetime, minutos_vigencia: int = 30) -> bool:
        """Valida si el QR sigue vigente"""
        ahora = datetime.utcnow()
        diferencia = ahora - created_at
        return diferencia.total_seconds() < (minutos_vigencia * 60)
    
    def obtener_datos_demo_yape(self) -> Dict[str, str]:
        """Retorna datos informativos para desarrollo/demo"""
        return {
            "merchant_name": self.YAPE_MERCHANT_NAME,
            "merchant_phone": self.YAPE_PHONE,
            "merchant_id": self.YAPE_MERCHANT_ID,
            "nota_desarrollo": (
                "En producción, integrar con API oficial de Yape "
                "o usar protocolo específico del proveedor de pagos"
            ),
            "instrucciones": [
                "1. Abre tu app Yape",
                "2. Toca 'Yapear'",
                "3. Escanea este código QR",
                "4. Confirma el monto",
                "5. Completa el pago",
                "6. Toma captura del comprobante"
            ]
        }

# ========================================
# FUNCIONES HELPER
# ========================================

async def generar_qr_pago(
    user_id: int,
    plan_codigo: str, 
    monto: Decimal
) -> Tuple[str, str, str]:
    """
    Helper function para generar QR completo
    
    Returns:
        Tuple[referencia, qr_data, qr_url]: Referencia, datos QR y URL Cloudinary
    """
    qr_service = QRYapeService()
    
    # Generar referencia única
    referencia = qr_service.generar_referencia_pago(user_id, plan_codigo)
    
    # Generar QR
    qr_data, qr_base64 = qr_service.generar_qr_yape(
        monto=monto,
        referencia=referencia,
        concepto=f"Suscripción {plan_codigo.title()} - Gallo App"
    )
    
    # Subir a Cloudinary
    qr_url = await qr_service.subir_qr_cloudinary(qr_base64, referencia, user_id)
    
    return referencia, qr_data, qr_url

def validar_monto_yape(monto: Decimal) -> bool:
    """Valida que el monto sea válido para Yape"""
    # Yape tiene límites: mínimo S/. 1.00, máximo S/. 500.00 por operación
    return 1.00 <= float(monto) <= 500.00

def obtener_instrucciones_pago() -> list:
    """Retorna instrucciones paso a paso para el usuario"""
    return [
        "📱 Abre tu aplicación Yape",
        "🎯 Selecciona 'Yapear' o 'Pagar'", 
        "📷 Escanea este código QR con tu cámara",
        "💰 Verifica que el monto sea correcto",
        "✅ Confirma el pago en tu app",
        "📸 Toma captura del comprobante de pago",
        "📤 Sube la captura en la siguiente pantalla",
        "⏰ Tu plan se activará tras verificación (2-24 horas)"
    ]