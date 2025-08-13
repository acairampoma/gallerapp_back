# 📄🐓 SERVICIO ÉPICO DE GENERACIÓN DE PDFs
# Genera fichas profesionales de gallos con ReportLab

import os
import io
import base64
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib.colors import HexColor, Color
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.platypus.frames import Frame
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️ ReportLab no disponible - PDFs no se pueden generar")

class PDFService:
    """🔥 Servicio épico para generar PDFs profesionales"""
    
    def __init__(self):
        # Obtener path del directorio de templates
        self.base_dir = Path(__file__).parent.parent
        self.templates_dir = self.base_dir / "templates"
        
        # Configurar Jinja2
        if self.templates_dir.exists():
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(self.templates_dir)),
                autoescape=True
            )
            print(f"✅ Templates cargados desde: {self.templates_dir}")
        else:
            print(f"❌ Directorio de templates no encontrado: {self.templates_dir}")
            self.jinja_env = None
    
    def generar_ficha_gallo_pdf(self, datos_ficha: Dict[str, Any]) -> Optional[bytes]:
        """
        🔥 GENERA PDF ÉPICO DE FICHA DE GALLO
        
        Args:
            datos_ficha: Datos completos del gallo para la ficha
            
        Returns:
            bytes: PDF generado como bytes, o None si hay error
        """
        try:
            if not WEASYPRINT_AVAILABLE:
                print("❌ WeasyPrint no disponible")
                return None
            
            if not self.jinja_env:
                print("❌ Templates no configurados")
                return None
            
            print("🔥 Iniciando generación de PDF...")
            print(f"📊 Generando ficha para: {datos_ficha.get('gallo', {}).get('nombre', 'Sin nombre')}")
            
            # 1. CARGAR TEMPLATE
            template = self.jinja_env.get_template('ficha_gallo.html')
            
            # 2. PREPARAR DATOS PARA EL TEMPLATE
            context = {
                'gallo': datos_ficha.get('gallo', {}),
                'genealogia': datos_ficha.get('genealogia', {}),
                'estadisticas': datos_ficha.get('estadisticas', {}),
                'historial_peleas': datos_ficha.get('historial_peleas', []),
                'metadata': datos_ficha.get('metadata', {}),
            }
            
            # 3. RENDERIZAR HTML
            html_content = template.render(**context)
            print("✅ HTML renderizado exitosamente")
            
            # 4. CONFIGURAR WEASYPRINT
            html_doc = weasyprint.HTML(string=html_content, base_url=str(self.base_dir))
            
            # Configuración CSS específica para PDF
            css_config = weasyprint.CSS(string="""
                @page {
                    size: A4;
                    margin: 15mm;
                }
                
                body {
                    font-family: Arial, sans-serif;
                }
                
                /* Evitar saltos de página en elementos importantes */
                .main-section,
                .stats-section,
                .genealogy-section {
                    page-break-inside: avoid;
                }
                
                /* Mejorar calidad de imágenes en PDF */
                img {
                    max-width: 100%;
                    height: auto;
                    image-rendering: -webkit-optimize-contrast;
                }
            """)
            
            # 5. GENERAR PDF
            print("📄 Generando PDF con WeasyPrint...")
            pdf_bytes = html_doc.write_pdf(stylesheets=[css_config])
            
            print(f"✅ PDF generado exitosamente - Tamaño: {len(pdf_bytes)} bytes")
            return pdf_bytes
            
        except Exception as e:
            print(f"❌ Error generando PDF: {str(e)}")
            print(f"❌ Tipo de error: {type(e).__name__}")
            import traceback
            print(f"❌ Stack trace: {traceback.format_exc()}")
            return None
    
    def generar_pdf_base64(self, datos_ficha: Dict[str, Any]) -> Optional[str]:
        """
        📄 GENERA PDF Y LO RETORNA COMO BASE64
        
        Útil para enviar PDFs directamente en APIs sin guardar archivos
        """
        try:
            pdf_bytes = self.generar_ficha_gallo_pdf(datos_ficha)
            
            if pdf_bytes:
                pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
                print(f"✅ PDF convertido a base64 - Longitud: {len(pdf_base64)}")
                return pdf_base64
            
            return None
            
        except Exception as e:
            print(f"❌ Error generando PDF base64: {str(e)}")
            return None
    
    def guardar_pdf_temporal(self, datos_ficha: Dict[str, Any], nombre_archivo: str = None) -> Optional[str]:
        """
        💾 GUARDA PDF EN DIRECTORIO TEMPORAL
        
        Args:
            datos_ficha: Datos para generar el PDF
            nombre_archivo: Nombre del archivo (opcional)
            
        Returns:
            str: Path del archivo guardado, o None si hay error
        """
        try:
            if not nombre_archivo:
                gallo_nombre = datos_ficha.get('gallo', {}).get('nombre', 'gallo')
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nombre_archivo = f"ficha_{gallo_nombre}_{timestamp}.pdf"
            
            # Limpiar nombre de archivo
            nombre_archivo = "".join(c for c in nombre_archivo if c.isalnum() or c in "._-")
            
            pdf_bytes = self.generar_ficha_gallo_pdf(datos_ficha)
            
            if pdf_bytes:
                # Crear directorio temporal si no existe
                temp_dir = self.base_dir / "temp_pdfs"
                temp_dir.mkdir(exist_ok=True)
                
                file_path = temp_dir / nombre_archivo
                
                with open(file_path, 'wb') as f:
                    f.write(pdf_bytes)
                
                print(f"✅ PDF guardado en: {file_path}")
                return str(file_path)
            
            return None
            
        except Exception as e:
            print(f"❌ Error guardando PDF temporal: {str(e)}")
            return None
    
    @staticmethod
    def verificar_dependencias() -> Dict[str, bool]:
        """🔍 VERIFICA SI TODAS LAS DEPENDENCIAS ESTÁN DISPONIBLES"""
        try:
            import weasyprint
            weasyprint_ok = True
        except ImportError:
            weasyprint_ok = False
        
        try:
            import jinja2
            jinja_ok = True
        except ImportError:
            jinja_ok = False
        
        return {
            "weasyprint": weasyprint_ok,
            "jinja2": jinja_ok,
            "todo_ok": weasyprint_ok and jinja_ok
        }
    
    def test_generacion(self) -> bool:
        """🧪 TEST BÁSICO DE GENERACIÓN DE PDF"""
        try:
            print("🧪 Ejecutando test de generación de PDF...")
            
            # Datos de prueba
            datos_test = {
                "gallo": {
                    "id": 1,
                    "nombre": "Gallo Test",
                    "codigo": "TEST-001",
                    "raza": "Test Breed",
                    "fecha_nacimiento": "2023-01-01",
                    "peso": "2.5 kg",
                    "color": "Colorado",
                    "estado": "Activo",
                    "criador": "Test Criador",
                    "propietario": "Test Propietario",
                    "foto_url": None
                },
                "estadisticas": {
                    "total_peleas": 5,
                    "peleas_ganadas": 3,
                    "peleas_perdidas": 2,
                    "efectividad": 60.0,
                    "ingresos_totales": 1500.0,
                    "total_topes": 10
                },
                "genealogia": {
                    "padre": None,
                    "madre": None
                },
                "historial_peleas": [
                    {
                        "fecha": "2023-06-15",
                        "lugar": "Coliseo Test",
                        "contrincante": "Rival 1",
                        "resultado": "ganada",
                        "tiempo": "15 min",
                        "premio": 500.0
                    }
                ],
                "metadata": {
                    "fecha_generacion": datetime.now().isoformat(),
                    "usuario_id": 1,
                    "tipo_reporte": "ficha_completa",
                    "version": "v1.0"
                }
            }
            
            pdf_bytes = self.generar_ficha_gallo_pdf(datos_test)
            
            if pdf_bytes and len(pdf_bytes) > 1000:  # PDF debe tener al menos 1KB
                print(f"✅ Test exitoso - PDF generado: {len(pdf_bytes)} bytes")
                return True
            else:
                print("❌ Test fallido - PDF muy pequeño o vacío")
                return False
                
        except Exception as e:
            print(f"❌ Test fallido con error: {str(e)}")
            return False


# 🔥 INSTANCIA GLOBAL DEL SERVICIO
pdf_service = PDFService()