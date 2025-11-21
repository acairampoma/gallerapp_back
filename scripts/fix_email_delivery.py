#!/usr/bin/env python3
"""
🔧 SCRIPT DE DIAGNÓSTICO Y CORRECCIÓN - ENTREGA DE CORREO
Específicamente para problemas con Hotmail/Outlook

Autor: JSALASINNOVATECH
Fecha: 2025-11-21
"""
import smtplib
import dns.resolver
import socket
import requests
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ssl
import time
from typing import Dict, List, Any

class EmailDeliveryFixer:
    def __init__(self):
        self.domain = "jsinnovatech.com"
        self.smtp_host = "mail.jsinnovatech.com"
        self.smtp_port = 587
        self.smtp_user = "sistemas@jsinnovatech.com"
        self.smtp_password = "Joa420188*"
        self.results = {}

    def check_dns_records(self) -> Dict[str, Any]:
        """🔍 Verificar registros DNS críticos"""
        print("🔍 Verificando registros DNS...")
        dns_results = {}
        
        try:
            # 1. Verificar MX Records
            try:
                mx_records = dns.resolver.resolve(self.domain, 'MX')
                dns_results['mx_records'] = [str(mx) for mx in mx_records]
                print(f"✅ MX Records encontrados: {dns_results['mx_records']}")
            except Exception as e:
                dns_results['mx_records'] = f"❌ Error: {e}"
                print(f"❌ Error MX: {e}")

            # 2. Verificar SPF Record
            try:
                txt_records = dns.resolver.resolve(self.domain, 'TXT')
                spf_found = False
                for txt in txt_records:
                    txt_str = str(txt).strip('"')
                    if txt_str.startswith('v=spf1'):
                        dns_results['spf_record'] = txt_str
                        spf_found = True
                        print(f"✅ SPF Record: {txt_str}")
                        break
                
                if not spf_found:
                    dns_results['spf_record'] = "❌ SPF Record NO ENCONTRADO"
                    print("❌ SPF Record NO ENCONTRADO")
                    
            except Exception as e:
                dns_results['spf_record'] = f"❌ Error: {e}"
                print(f"❌ Error SPF: {e}")

            # 3. Verificar DKIM Records (selector común)
            dkim_selectors = ['default', 'mail', 'dkim', 'selector1', 'selector2']
            dns_results['dkim_records'] = {}
            
            for selector in dkim_selectors:
                try:
                    dkim_domain = f"{selector}._domainkey.{self.domain}"
                    dkim_records = dns.resolver.resolve(dkim_domain, 'TXT')
                    for dkim in dkim_records:
                        dkim_str = str(dkim).strip('"')
                        if 'k=rsa' in dkim_str or 'v=DKIM1' in dkim_str:
                            dns_results['dkim_records'][selector] = dkim_str
                            print(f"✅ DKIM ({selector}): Encontrado")
                            break
                except:
                    continue
                    
            if not dns_results['dkim_records']:
                dns_results['dkim_records'] = "❌ DKIM Records NO ENCONTRADOS"
                print("❌ DKIM Records NO ENCONTRADOS")

            # 4. Verificar DMARC Record
            try:
                dmarc_domain = f"_dmarc.{self.domain}"
                dmarc_records = dns.resolver.resolve(dmarc_domain, 'TXT')
                for dmarc in dmarc_records:
                    dmarc_str = str(dmarc).strip('"')
                    if dmarc_str.startswith('v=DMARC1'):
                        dns_results['dmarc_record'] = dmarc_str
                        print(f"✅ DMARC Record: {dmarc_str}")
                        break
            except Exception as e:
                dns_results['dmarc_record'] = "❌ DMARC Record NO ENCONTRADO"
                print("❌ DMARC Record NO ENCONTRADO")

        except Exception as e:
            print(f"❌ Error general DNS: {e}")
            
        self.results['dns'] = dns_results
        return dns_results

    def check_server_ip_reputation(self) -> Dict[str, Any]:
        """🔍 Verificar reputación de IP del servidor"""
        print("\n🔍 Verificando reputación de IP...")
        ip_results = {}
        
        try:
            # Obtener IP del servidor SMTP
            server_ip = socket.gethostbyname(self.smtp_host)
            ip_results['server_ip'] = server_ip
            print(f"📍 IP del servidor: {server_ip}")
            
            # Verificar blacklists comunes
            blacklists = [
                'zen.spamhaus.org',
                'bl.spamcop.net', 
                'b.barracudacentral.org',
                'dnsbl.sorbs.net'
            ]
            
            ip_results['blacklist_status'] = {}
            ip_octets = server_ip.split('.')
            reversed_ip = '.'.join(reversed(ip_octets))
            
            for bl in blacklists:
                try:
                    query = f"{reversed_ip}.{bl}"
                    dns.resolver.resolve(query, 'A')
                    ip_results['blacklist_status'][bl] = "❌ LISTADO"
                    print(f"❌ {bl}: LISTADO")
                except:
                    ip_results['blacklist_status'][bl] = "✅ LIMPIO" 
                    print(f"✅ {bl}: LIMPIO")
                    
        except Exception as e:
            ip_results['error'] = str(e)
            print(f"❌ Error verificando IP: {e}")
            
        self.results['ip_reputation'] = ip_results
        return ip_results

    def test_smtp_connection(self) -> Dict[str, Any]:
        """🔍 Probar conexión SMTP detallada"""
        print("\n🔍 Probando conexión SMTP...")
        smtp_results = {}
        
        try:
            # Test conexión básica
            print(f"📡 Conectando a {self.smtp_host}:{self.smtp_port}")
            
            server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30)
            server.set_debuglevel(1)  # Ver conversación SMTP
            
            # Información del servidor
            smtp_results['server_response'] = server.ehlo()[1].decode()
            print(f"🔗 Respuesta servidor: {smtp_results['server_response'][:100]}...")
            
            # Test STARTTLS
            print("🔒 Iniciando STARTTLS...")
            server.starttls()
            smtp_results['tls_support'] = "✅ STARTTLS OK"
            print("✅ STARTTLS exitoso")
            
            # Test autenticación
            print("🔐 Probando autenticación...")
            server.login(self.smtp_user, self.smtp_password)
            smtp_results['auth_status'] = "✅ Autenticación exitosa"
            print("✅ Autenticación exitosa")
            
            server.quit()
            smtp_results['connection_status'] = "✅ Conexión completamente exitosa"
            
        except smtplib.SMTPAuthenticationError as e:
            smtp_results['auth_status'] = f"❌ Error autenticación: {e}"
            print(f"❌ Error autenticación: {e}")
        except smtplib.SMTPConnectError as e:
            smtp_results['connection_status'] = f"❌ Error conexión: {e}"
            print(f"❌ Error conexión: {e}")
        except Exception as e:
            smtp_results['general_error'] = f"❌ Error general: {e}"
            print(f"❌ Error general: {e}")
            
        self.results['smtp_test'] = smtp_results
        return smtp_results

    def test_email_to_hotmail(self, test_email: str = "alancairampoma@hotmail.com") -> Dict[str, Any]:
        """📧 Enviar email de prueba específicamente a Hotmail"""
        print(f"\n📧 Enviando email de prueba a {test_email}...")
        test_results = {}
        
        try:
            # Crear mensaje optimizado para Hotmail/Outlook
            msg = MIMEMultipart('alternative')
            
            # Headers críticos para Hotmail/Outlook
            msg['Subject'] = "Prueba de Entrega - Sistema Gallistico"
            msg['From'] = f"Sistemas Gallistico <{self.smtp_user}>"
            msg['To'] = test_email
            msg['Message-ID'] = f"<test-{int(time.time())}@{self.domain}>"
            msg['Date'] = time.strftime('%a, %d %b %Y %H:%M:%S %z')
            msg['X-Priority'] = "3"
            msg['X-Mailer'] = "Gallistico Email System v1.0"
            
            # Contenido optimizado (sin emojis)
            texto_plano = """
Prueba de Entrega de Email - Sistema Gallistico

Este es un mensaje de prueba para verificar la entrega correcta
de correos desde nuestro servidor SMTP propio a cuentas de Hotmail/Outlook.

Si recibes este mensaje, la configuracion esta funcionando correctamente.

Saludos,
Equipo Tecnico Gallistico
"""
            
            html_optimizado = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Prueba Sistema Gallistico</title>
</head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
        <h2 style="color: #2c3e50;">Prueba de Entrega - Sistema Gallistico</h2>
        <p style="color: #555; line-height: 1.6;">
            Este es un mensaje de prueba para verificar la entrega correcta
            de correos desde nuestro servidor SMTP propio a cuentas de Hotmail/Outlook.
        </p>
        <div style="background: white; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p><strong>Detalles del test:</strong></p>
            <ul>
                <li>Servidor: mail.jsinnovatech.com</li>
                <li>Protocolo: SMTP+STARTTLS</li>
                <li>Puerto: 587</li>
                <li>Dominio: jsinnovatech.com</li>
            </ul>
        </div>
        <p style="color: #777; font-size: 14px;">
            Si recibes este mensaje, la configuracion esta funcionando correctamente.
        </p>
        <hr>
        <p style="color: #999; font-size: 12px;">
            Equipo Tecnico Gallistico<br>
            Este mensaje fue generado automaticamente
        </p>
    </div>
</body>
</html>"""
            
            # Adjuntar contenido
            parte_texto = MIMEText(texto_plano, 'plain', 'utf-8')
            parte_html = MIMEText(html_optimizado, 'html', 'utf-8')
            msg.attach(parte_texto)
            msg.attach(parte_html)
            
            # Enviar
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                resultado = server.send_message(msg)
                
                test_results['status'] = "✅ Email enviado exitosamente"
                test_results['smtp_result'] = str(resultado)
                test_results['target_email'] = test_email
                print(f"✅ Email enviado exitosamente a {test_email}")
                
        except Exception as e:
            test_results['status'] = f"❌ Error enviando: {e}"
            test_results['error'] = str(e)
            print(f"❌ Error enviando email: {e}")
            
        self.results['email_test'] = test_results
        return test_results

    def generate_dns_recommendations(self) -> List[str]:
        """📋 Generar recomendaciones de configuración DNS"""
        print("\n📋 Generando recomendaciones DNS...")
        
        recommendations = []
        
        # Verificar si necesita SPF
        dns_info = self.results.get('dns', {})
        spf_record = dns_info.get('spf_record', '')
        
        if '❌' in str(spf_record) or not spf_record:
            recommendations.append({
                'type': 'SPF Record',
                'action': 'Agregar registro TXT en DNS',
                'record': f'v=spf1 mx a include:_spf.{self.domain} ip4:{self.results.get("ip_reputation", {}).get("server_ip", "IP_SERVIDOR")} ~all',
                'priority': 'ALTA - Crítico para Hotmail/Outlook'
            })
            
        if '❌' in str(dns_info.get('dkim_records', '')):
            recommendations.append({
                'type': 'DKIM Record',
                'action': 'Configurar DKIM en servidor de correo',
                'details': 'Generar claves DKIM y publicar registro TXT',
                'priority': 'ALTA - Mejora significativamente la entrega'
            })
            
        if '❌' in str(dns_info.get('dmarc_record', '')):
            recommendations.append({
                'type': 'DMARC Record', 
                'action': 'Agregar registro TXT en DNS',
                'record': f'v=DMARC1; p=quarantine; rua=mailto:dmarc@{self.domain}; ruf=mailto:dmarc@{self.domain}; sp=quarantine; adkim=r; aspf=r;',
                'priority': 'MEDIA - Importante para reputación'
            })
            
        return recommendations

    def run_full_diagnosis(self, test_email: str = None) -> Dict[str, Any]:
        """🔧 Ejecutar diagnóstico completo"""
        print("=" * 60)
        print("🔧 DIAGNÓSTICO COMPLETO - ENTREGA DE CORREO")
        print("=" * 60)
        
        # 1. Verificar DNS
        self.check_dns_records()
        
        # 2. Verificar reputación IP
        self.check_server_ip_reputation()
        
        # 3. Probar conexión SMTP
        self.test_smtp_connection()
        
        # 4. Enviar email de prueba si se especifica
        if test_email:
            self.test_email_to_hotmail(test_email)
            
        # 5. Generar recomendaciones
        recommendations = self.generate_dns_recommendations()
        self.results['recommendations'] = recommendations
        
        # 6. Resumen final
        print("\n" + "=" * 60)
        print("📊 RESUMEN FINAL")
        print("=" * 60)
        
        for rec in recommendations:
            print(f"🔹 {rec['type']}: {rec['action']}")
            if 'record' in rec:
                print(f"   📝 Registro: {rec['record']}")
            print(f"   ⚠️ Prioridad: {rec['priority']}\n")
            
        return self.results

def main():
    """🚀 Función principal"""
    fixer = EmailDeliveryFixer()
    
    # Ejecutar diagnóstico completo
    resultados = fixer.run_full_diagnosis(test_email="alancairampoma@hotmail.com")
    
    # Guardar resultados en archivo
    with open('email_diagnosis_results.json', 'w', encoding='utf-8') as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)
        
    print(f"\n💾 Resultados guardados en: email_diagnosis_results.json")
    print("📧 Revisa si el email de prueba llegó a la bandeja o spam")
    
    return resultados

if __name__ == "__main__":
    main()
