# 🐓 GalloApp Pro Backend

## 🚀 Backend FastAPI para Gestión de Gallos de Pelea

### 📦 Instalación

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno (Windows)
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 🌐 Endpoints

- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/health

### 🗄️ Base de Datos

- **PostgreSQL Railway**
- **Switch automático** local/cloud

### 📸 Cloudinary

- **Upload automático** JPG → WebP
- **CDN global** para imágenes y videos

### 🚂 Deploy Railway

```bash
railway login
railway link
railway up
```
