from decouple import config
from typing import List

class Settings:
    # 🔐 JWT Configuration
    SECRET_KEY: str = config("SECRET_KEY", default="galloapp-super-secret-key-development")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # 🗄️ Database
    DATABASE_URL: str = config(
        "DATABASE_URL", 
        default="postgresql://postgres:KfktiHjbugWVTzvalfwxiVZwsvVFatrk@gondola.proxy.rlwy.net:54162/railway"
    )
    
    # 📸 Cloudinary
    CLOUDINARY_CLOUD_NAME: str = config("CLOUDINARY_CLOUD_NAME", default="dz4czc3en")
    CLOUDINARY_API_KEY: str = config("CLOUDINARY_API_KEY", default="455285241939111")
    CLOUDINARY_API_SECRET: str = config("CLOUDINARY_API_SECRET", default="1uzQrkFD1Rbj8vPOClFBUEIwBn0")
    
    # 📧 SendGrid Email Service
    SENDGRID_API_KEY: str = config("SENDGRID_API_KEY")
    SENDGRID_FROM_EMAIL: str = config("SENDGRID_FROM_EMAIL", default="alancairampoma@gmail.com")
    SENDGRID_FROM_NAME: str = config("SENDGRID_FROM_NAME", default="Casta de Gallos")
    
    # 🌐 CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # 🔄 Environment
    ENVIRONMENT: str = config("ENVIRONMENT", default="local")

settings = Settings()
