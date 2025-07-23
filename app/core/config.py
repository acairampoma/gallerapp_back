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
    
    # 🌐 CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # 🔄 Environment
    ENVIRONMENT: str = config("ENVIRONMENT", default="local")

settings = Settings()
