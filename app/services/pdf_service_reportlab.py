# 📄🐓 SERVICIO ÉPICO DE GENERACIÓN DE PDFs CON REPORTLAB
# Compatible con Railway - Sin dependencias del sistema

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
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("WARNING: ReportLab no disponible - PDFs no se pueden generar")

class PDFServiceReportLab:
    """🔥 Servicio épico para generar PDFs profesionales con ReportLab"""
    
    def __init__(self):
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab no está disponible")
            
        # Colores épicos de Casto de Gallos
        self.primary_color = HexColor('#2c5530')
        self.success_color = HexColor('#4CAF50')
        self.warning_color = HexColor('#FF9800')
        self.error_color = HexColor('#F44336')
        
        # Configurar estilos
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """🎨 Configurar estilos personalizados"""
        
        # Título principal
        self.styles.add(ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=self.primary_color,
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.grey,
            alignment=TA_CENTER,
            spaceAfter=15,
            fontName='Helvetica'
        ))
        
        # Sección
        self.styles.add(ParagraphStyle(
            'SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=self.primary_color,
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        ))
        
        # Texto normal con más espacio
        self.styles.add(ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            fontName='Helvetica'
        ))
        
        # Para datos importantes
        self.styles.add(ParagraphStyle(
            'DataValue',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.primary_color,
            fontName='Helvetica-Bold'
        ))
    
    def generar_ficha_gallo_pdf(self, datos_ficha: Dict[str, Any]) -> Optional[bytes]:
        """
        🔥 GENERA PDF ÉPICO DE FICHA DE GALLO CON REPORTLAB
        
        Args:
            datos_ficha: Datos completos del gallo para la ficha
            
        Returns:
            bytes: PDF generado como bytes, o None si hay error
        """
        try:
            if not REPORTLAB_AVAILABLE:
                print("❌ ReportLab no disponible")
                return None
            
            print("🔥 Iniciando generación de PDF con ReportLab...")
            
            gallo = datos_ficha.get('gallo', {})
            estadisticas = datos_ficha.get('estadisticas', {})
            genealogia = datos_ficha.get('genealogia', {})
            historial = datos_ficha.get('historial_peleas', [])
            metadata = datos_ficha.get('metadata', {})
            
            print(f"📊 Generando ficha para: {gallo.get('nombre', 'Sin nombre')}")
            
            # Crear buffer en memoria
            buffer = io.BytesIO()
            
            # Crear documento PDF
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # Construir contenido
            story = []
            
            # 🔥 HEADER ÉPICO
            story.append(Paragraph("🐓 CASTO DE GALLOS", self.styles['CustomTitle']))
            story.append(Paragraph(f"Ficha Técnica Profesional", self.styles['CustomSubtitle']))
            story.append(Spacer(1, 20))
            
            # 📊 INFORMACIÓN PRINCIPAL DEL GALLO
            story.append(Paragraph("📊 INFORMACIÓN PRINCIPAL", self.styles['SectionTitle']))
            
            # Tabla de información básica
            info_data = [
                ['Nombre:', gallo.get('nombre', 'N/A')],
                ['Código:', gallo.get('codigo', 'N/A')],
                ['Raza:', gallo.get('raza', 'No especificada')],
                ['Fecha Nacimiento:', gallo.get('fecha_nacimiento', 'No registrada')],
                ['Peso:', gallo.get('peso', 'No registrado')],
                ['Color:', gallo.get('color', 'No especificado')],
                ['Estado:', gallo.get('estado', 'Activo')],
                ['Criador:', gallo.get('criador', 'No registrado')],
                ['Propietario:', gallo.get('propietario', 'No registrado')]
            ]
            
            info_table = Table(info_data, colWidths=[4*cm, 8*cm])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), HexColor('#f8f9fa')),
                ('TEXTCOLOR', (0, 0), (0, -1), self.primary_color),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, HexColor('#f8f9fa')])
            ]))
            
            story.append(info_table)
            story.append(Spacer(1, 20))
            
            # 🏆 ESTADÍSTICAS ÉPICAS
            story.append(Paragraph("🏆 ESTADÍSTICAS DE RENDIMIENTO", self.styles['SectionTitle']))
            
            stats_data = [
                ['Métrica', 'Valor'],
                ['Total Peleas', str(estadisticas.get('total_peleas', 0))],
                ['Peleas Ganadas', str(estadisticas.get('peleas_ganadas', 0))],
                ['Peleas Perdidas', str(estadisticas.get('peleas_perdidas', 0))],
                ['Efectividad', f"{estadisticas.get('efectividad', 0):.1f}%"],
                ['Ingresos Totales', f"S/ {estadisticas.get('ingresos_totales', 0):.2f}"],
                ['Total Topes', str(estadisticas.get('total_topes', 0))]
            ]
            
            stats_table = Table(stats_data, colWidths=[6*cm, 6*cm])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f0f8ff')])
            ]))
            
            story.append(stats_table)
            story.append(Spacer(1, 20))
            
            # 🧬 GENEALOGÍA
            if genealogia.get('padre') or genealogia.get('madre'):
                story.append(Paragraph("🧬 GENEALOGÍA", self.styles['SectionTitle']))
                
                genealogy_data = [['Relación', 'Nombre', 'Código', 'Raza']]
                
                if genealogia.get('padre'):
                    padre = genealogia['padre']
                    genealogy_data.append([
                        '👨 Padre',
                        padre.get('nombre', 'N/A'),
                        padre.get('codigo', 'N/A'),
                        padre.get('raza', 'N/A')
                    ])
                
                if genealogia.get('madre'):
                    madre = genealogia['madre']
                    genealogy_data.append([
                        '👩 Madre',
                        madre.get('nombre', 'N/A'),
                        madre.get('codigo', 'N/A'),
                        madre.get('raza', 'N/A')
                    ])
                
                genealogy_table = Table(genealogy_data, colWidths=[3*cm, 4*cm, 3*cm, 3*cm])
                genealogy_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#f0f8f0'), colors.white])
                ]))
                
                story.append(genealogy_table)
                story.append(Spacer(1, 20))
            
            # 📜 HISTORIAL DE PELEAS
            if historial:
                story.append(Paragraph("📜 HISTORIAL DE PELEAS (Últimas 10)", self.styles['SectionTitle']))
                
                historial_data = [['Fecha', 'Lugar', 'Contrincante', 'Resultado', 'Premio']]
                
                for pelea in historial[:10]:  # Máximo 10 peleas
                    resultado = pelea.get('resultado', 'N/A')
                    premio = pelea.get('premio', 0)
                    
                    historial_data.append([
                        pelea.get('fecha', 'N/A')[:10] if pelea.get('fecha') else 'N/A',  # Solo fecha, sin hora
                        pelea.get('lugar', 'N/A'),
                        pelea.get('contrincante', 'N/A'),
                        resultado.upper() if resultado else 'N/A',
                        f"S/ {premio:.2f}" if premio else 'S/ 0.00'
                    ])
                
                historial_table = Table(historial_data, colWidths=[2.5*cm, 3*cm, 3*cm, 2*cm, 2*cm])
                historial_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#fff8dc')])
                ]))
                
                story.append(historial_table)
                story.append(Spacer(1, 20))
            
            # 📝 FOOTER
            story.append(Spacer(1, 30))
            story.append(Paragraph("🐓 CASTO DE GALLOS - Sistema Profesional de Gestión", self.styles['CustomSubtitle']))
            
            footer_text = f"""
            Ficha generada el {metadata.get('fecha_generacion', datetime.now().isoformat())[:19]} | 
            Usuario ID: {metadata.get('usuario_id', 'N/A')} | 
            Versión: {metadata.get('version', 'v1.0')}
            """
            story.append(Paragraph(footer_text, self.styles['CustomNormal']))
            
            # Construir PDF
            print("📄 Construyendo PDF con ReportLab...")
            doc.build(story)
            
            # Obtener bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
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
                base_dir = Path(__file__).parent.parent
                temp_dir = base_dir / "temp_pdfs"
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
        return {
            "reportlab": REPORTLAB_AVAILABLE,
            "todo_ok": REPORTLAB_AVAILABLE
        }
    
    def generar_relacion_peleas_pdf(self, datos_evento: Dict[str, Any]) -> Optional[bytes]:
        """
        🥊 GENERA PDF DE RELACIÓN DE PELEAS DE UN EVENTO

        Args:
            datos_evento: Diccionario con:
                - evento: {titulo, fecha_evento, coliseo_nombre, descripcion}
                - peleas: [{numero_pelea, titulo_pelea, galpon_izquierda, gallo_izquierda_nombre,
                           galpon_derecha, gallo_derecha_nombre, hora_inicio_estimada, resultado}]
                - metadata: {fecha_generacion, usuario_id, version}

        Returns:
            bytes: PDF generado como bytes, o None si hay error
        """
        try:
            if not REPORTLAB_AVAILABLE:
                print("❌ ReportLab no disponible")
                return None

            print("🥊 Iniciando generación de PDF de Relación de Peleas...")

            evento = datos_evento.get('evento', {})
            peleas = datos_evento.get('peleas', [])
            metadata = datos_evento.get('metadata', {})

            print(f"📊 Generando relación para evento: {evento.get('titulo', 'Sin título')}")
            print(f"📊 Total de peleas: {len(peleas)}")

            # Crear buffer en memoria
            buffer = io.BytesIO()

            # Crear documento PDF
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )

            # Construir contenido
            story = []

            # 🔥 HEADER ÉPICO
            story.append(Paragraph("🥊 RELACIÓN DE PELEAS", self.styles['CustomTitle']))
            story.append(Spacer(1, 10))

            # 📋 INFORMACIÓN DEL EVENTO (CABECERA)
            story.append(Paragraph("📋 DATOS DEL EVENTO", self.styles['SectionTitle']))

            # Formatear fecha
            fecha_evento = evento.get('fecha_evento', 'No registrada')
            if fecha_evento and fecha_evento != 'No registrada':
                try:
                    from datetime import datetime
                    fecha_dt = datetime.fromisoformat(fecha_evento.replace('Z', '+00:00'))
                    fecha_evento = fecha_dt.strftime('%d/%m/%Y')
                except:
                    pass

            # Tabla de información del evento
            evento_data = [
                ['Título:', evento.get('titulo', 'Sin título')],
                ['Fecha:', fecha_evento],
                ['Coliseo:', evento.get('coliseo_nombre', 'No especificado')],
                ['Descripción:', evento.get('descripcion', 'Sin descripción')],
                ['Total Peleas:', str(len(peleas))]
            ]

            evento_table = Table(evento_data, colWidths=[4*cm, 12*cm])
            evento_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), HexColor('#f8f9fa')),
                ('TEXTCOLOR', (0, 0), (0, -1), self.primary_color),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, HexColor('#f8f9fa')])
            ]))

            story.append(evento_table)
            story.append(Spacer(1, 20))

            # 🥊 DETALLE DE PELEAS
            if peleas:
                story.append(Paragraph("🥊 DETALLE DE PELEAS", self.styles['SectionTitle']))

                # Encabezado de tabla
                peleas_data = [['#', 'Título', 'Galpón Izq.', 'Gallo Izq.', 'Galpón Der.', 'Gallo Der.', 'Hora', 'Resultado']]

                for pelea in peleas:
                    # Formatear hora
                    hora = pelea.get('hora_inicio_estimada', '-')
                    if hora and hora != '-':
                        try:
                            # Si viene como time object o string HH:MM:SS
                            if isinstance(hora, str) and len(hora) >= 5:
                                hora = hora[:5]  # Tomar solo HH:MM
                        except:
                            pass

                    # Formatear resultado
                    resultado = pelea.get('resultado', 'Pendiente')
                    if resultado == 'izquierda':
                        resultado = '← Izq.'
                    elif resultado == 'derecha':
                        resultado = 'Der. →'
                    elif resultado == 'empate':
                        resultado = 'Empate'
                    else:
                        resultado = '-'

                    peleas_data.append([
                        str(pelea.get('numero_pelea', '')),
                        pelea.get('titulo_pelea', '')[:20] if pelea.get('titulo_pelea') else '',
                        pelea.get('galpon_izquierda', '')[:15] if pelea.get('galpon_izquierda') else '',
                        pelea.get('gallo_izquierda_nombre', '')[:15] if pelea.get('gallo_izquierda_nombre') else '',
                        pelea.get('galpon_derecha', '')[:15] if pelea.get('galpon_derecha') else '',
                        pelea.get('gallo_derecha_nombre', '')[:15] if pelea.get('gallo_derecha_nombre') else '',
                        hora,
                        resultado
                    ])

                peleas_table = Table(
                    peleas_data,
                    colWidths=[0.8*cm, 2.5*cm, 2.2*cm, 2.2*cm, 2.2*cm, 2.2*cm, 1.2*cm, 1.5*cm]
                )
                peleas_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f8f9fa')])
                ]))

                story.append(peleas_table)
            else:
                story.append(Paragraph("Sin peleas registradas en este evento", self.styles['CustomNormal']))

            story.append(Spacer(1, 30))

            # 📝 FOOTER
            story.append(Paragraph("🐓 CASTO DE GALLOS - Sistema Profesional de Gestión", self.styles['CustomSubtitle']))

            footer_text = f"""
            Documento generado el {metadata.get('fecha_generacion', datetime.now().isoformat())[:19]} |
            Usuario ID: {metadata.get('usuario_id', 'N/A')} |
            Versión: {metadata.get('version', 'v1.0')}
            """
            story.append(Paragraph(footer_text, self.styles['CustomNormal']))

            # Construir PDF
            print("📄 Construyendo PDF con ReportLab...")
            doc.build(story)

            # Obtener bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()

            print(f"✅ PDF generado exitosamente - Tamaño: {len(pdf_bytes)} bytes")
            return pdf_bytes

        except Exception as e:
            print(f"❌ Error generando PDF de peleas: {str(e)}")
            print(f"❌ Tipo de error: {type(e).__name__}")
            import traceback
            print(f"❌ Stack trace: {traceback.format_exc()}")
            return None

    def test_generacion(self) -> bool:
        """🧪 TEST BÁSICO DE GENERACIÓN DE PDF"""
        try:
            print("🧪 Ejecutando test de generación de PDF con ReportLab...")

            # Datos de prueba
            datos_test = {
                "gallo": {
                    "id": 1,
                    "nombre": "Gallo Test ReportLab",
                    "codigo": "TEST-001",
                    "raza": "Test Breed",
                    "fecha_nacimiento": "2023-01-01",
                    "peso": "2.5 kg",
                    "color": "Colorado",
                    "estado": "Activo",
                    "criador": "Test Criador",
                    "propietario": "Test Propietario"
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
                    "padre": {
                        "nombre": "Padre Test",
                        "codigo": "PADRE-001",
                        "raza": "Raza Padre"
                    },
                    "madre": {
                        "nombre": "Madre Test",
                        "codigo": "MADRE-001",
                        "raza": "Raza Madre"
                    }
                },
                "historial_peleas": [
                    {
                        "fecha": "2023-06-15",
                        "lugar": "Coliseo Test",
                        "contrincante": "Rival 1",
                        "resultado": "ganada",
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


# 🔥 INSTANCIA GLOBAL DEL SERVICIO REPORTLAB
try:
    pdf_service_reportlab = PDFServiceReportLab()
except ImportError:
    pdf_service_reportlab = None
    print("WARNING: PDFServiceReportLab no disponible - usando servicio alternativo")