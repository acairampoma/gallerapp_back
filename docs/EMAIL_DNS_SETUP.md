# 🔧 CONFIGURACIÓN DNS PARA MEJORAR ENTREGA DE CORREO

## 📋 REGISTROS DNS NECESARIOS PARA JSINNOVATECH.COM

### **PROBLEMA IDENTIFICADO**
Los correos no llegan a **Hotmail/Outlook** porque faltan registros DNS críticos de autenticación.

---

## **1. 📧 REGISTRO SPF (Sender Policy Framework)**

**¿Qué hace?** Autoriza qué servidores pueden enviar correos desde tu dominio.

**Registro a agregar:**
```
Tipo: TXT
Nombre: jsinnovatech.com (o @)
Valor: v=spf1 mx a include:mail.jsinnovatech.com ip4:[IP_DEL_SERVIDOR] ~all
```

**¿Dónde obtener IP_DEL_SERVIDOR?**
Ejecuta este comando en tu servidor:
```bash
nslookup mail.jsinnovatech.com
```

**Ejemplo del registro final:**
```
v=spf1 mx a include:mail.jsinnovatech.com ip4:xxx.xxx.xxx.xxx ~all
```

---

## **2. 🔐 REGISTRO DKIM (DomainKeys Identified Mail)**

**¿Qué hace?** Firma digitalmente tus correos para verificar autenticidad.

### **Paso 1: Generar claves DKIM en tu servidor**

Conéctate a tu servidor de correo y ejecuta:

```bash
# Instalar opendkim si no está instalado
sudo apt-get install opendkim opendkim-tools

# Crear directorio para claves
sudo mkdir -p /etc/opendkim/keys/jsinnovatech.com

# Generar claves DKIM
sudo opendkim-genkey -t -s default -d jsinnovatech.com

# Mover claves al directorio correcto
sudo mv default.private /etc/opendkim/keys/jsinnovatech.com/
sudo mv default.txt /etc/opendkim/keys/jsinnovatech.com/

# Ver la clave pública para DNS
sudo cat /etc/opendkim/keys/jsinnovatech.com/default.txt
```

### **Paso 2: Configurar registro DNS DKIM**

**Registro a agregar:**
```
Tipo: TXT
Nombre: default._domainkey.jsinnovatech.com
Valor: [contenido del archivo default.txt]
```

El valor será algo como:
```
v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC... (clave larga)
```

---

## **3. 🛡️ REGISTRO DMARC (Domain Message Authentication)**

**¿Qué hace?** Define políticas sobre qué hacer con correos que fallan SPF/DKIM.

**Registro a agregar:**
```
Tipo: TXT
Nombre: _dmarc.jsinnovatech.com
Valor: v=DMARC1; p=quarantine; rua=mailto:dmarc@jsinnovatech.com; ruf=mailto:dmarc@jsinnovatech.com; sp=quarantine; adkim=r; aspf=r; fo=1;
```

**Explicación del registro:**
- `p=quarantine`: Poner en cuarentena correos sospechosos
- `rua=mailto:dmarc@jsinnovatech.com`: Reportes agregados
- `ruf=mailto:dmarc@jsinnovatech.com`: Reportes de fallos
- `adkim=r`: DKIM en modo relajado
- `aspf=r`: SPF en modo relajado

---

## **4. 🔄 REGISTRO PTR (Reverse DNS)**

**¿Qué hace?** Permite verificación reversa de IP a dominio.

**⚠️ IMPORTANTE:** Este registro debe configurarlo tu proveedor de hosting/VPS.

Contacta a tu proveedor y solicita:
```
IP del servidor → mail.jsinnovatech.com
```

---

## **5. ✅ VERIFICAR CONFIGURACIONES**

### **Herramientas de verificación:**

1. **SPF:** https://mxtoolbox.com/spf.aspx
2. **DKIM:** https://mxtoolbox.com/dkim.aspx 
3. **DMARC:** https://mxtoolbox.com/dmarc.aspx
4. **General:** https://mail-tester.com/

### **Comando para verificar desde terminal:**
```bash
# Verificar SPF
dig TXT jsinnovatech.com

# Verificar DKIM
dig TXT default._domainkey.jsinnovatech.com

# Verificar DMARC
dig TXT _dmarc.jsinnovatech.com

# Verificar MX
dig MX jsinnovatech.com
```

---

## **6. 📊 TIMELINE DE IMPLEMENTACIÓN**

| Prioridad | Registro | Tiempo estimado | Impacto en Hotmail/Outlook |
|-----------|----------|-----------------|----------------------------|
| 🔴 ALTA   | SPF      | 5 minutos      | +70% entrega              |
| 🔴 ALTA   | DKIM     | 30 minutos     | +20% entrega              |
| 🟡 MEDIA  | DMARC    | 10 minutos     | +10% reputación           |
| 🟢 BAJA   | PTR      | Contactar ISP  | +5% entrega               |

---

## **7. 🚀 CONFIGURACIÓN DE POSTFIX (Si usas Postfix)**

### **Configurar DKIM en Postfix:**

```bash
# Editar configuración principal
sudo nano /etc/postfix/main.cf

# Agregar estas líneas:
smtpd_milters = inet:localhost:12301
non_smtpd_milters = inet:localhost:12301
milter_default_action = accept
```

### **Configurar OpenDKIM:**

```bash
# Crear archivo de configuración
sudo nano /etc/opendkim.conf

# Contenido:
AutoRestart             Yes
AutoRestartRate         10/1h
Syslog                  Yes
SyslogSuccess           Yes
LogWhy                  Yes
Canonicalization        relaxed/simple
ExternalIgnoreList      refile:/etc/opendkim/TrustedHosts
InternalHosts           refile:/etc/opendkim/TrustedHosts
KeyTable                refile:/etc/opendkim/KeyTable
SigningTable            refile:/etc/opendkim/SigningTable
Mode                    sv
PidFile                 /var/run/opendkim/opendkim.pid
SignatureAlgorithm      rsa-sha256
UserID                  opendkim:opendkim
Socket                  inet:12301@localhost

# Crear archivos necesarios
sudo nano /etc/opendkim/TrustedHosts
# Contenido:
127.0.0.1
localhost
jsinnovatech.com

sudo nano /etc/opendkim/KeyTable
# Contenido:
default._domainkey.jsinnovatech.com jsinnovatech.com:default:/etc/opendkim/keys/jsinnovatech.com/default.private

sudo nano /etc/opendkim/SigningTable
# Contenido:
*@jsinnovatech.com default._domainkey.jsinnovatech.com

# Reiniciar servicios
sudo systemctl restart opendkim
sudo systemctl restart postfix
```

---

## **8. 🧪 SCRIPT DE PRUEBA**

Usa el script `fix_email_delivery.py` que he creado:

```bash
cd /ruta/a/tu/proyecto
python scripts/fix_email_delivery.py
```

Este script te dirá exactamente qué registros DNS faltan y cómo configurarlos.

---

## **9. ⚠️ NOTAS IMPORTANTES**

1. **Propagación DNS:** Los cambios pueden tardar hasta 24-48 horas en propagarse.
2. **Hotmail/Outlook es estricto:** Requieren SPF y DKIM para buena entrega.
3. **No uses `-all` en SPF:** Usa `~all` para permitir soft-fail.
4. **Monitorea reportes DMARC:** Te ayudarán a detectar problemas.

---

## **10. 🆘 SOLUCIÓN RÁPIDA SI TIENES PRISA**

Si necesitas una solución temporal mientras configuras DNS:

1. **Cambia el FROM a un dominio verificado** (como Gmail)
2. **Usa SendGrid o similar** como servicio externo
3. **Configura Railway con variables de entorno** para servicio externo

### **Variables para Railway:**
```
USE_SMTP=false
SENDGRID_API_KEY=tu_api_key
SENDGRID_FROM_EMAIL=verificado@gmail.com
```

---

¡Con estos cambios, tus correos deberían llegar correctamente a Hotmail/Outlook! 📧✅
