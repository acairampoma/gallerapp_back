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

    # 🎬 ImageKit (para videos de evento x peleas)
    IMAGEKIT_PRIVATE_KEY: str = config("IMAGEKIT_PRIVATE_KEY", default="private_FChdQz74nrcLIWrOxd9+tWXNSWA=")
    IMAGEKIT_PUBLIC_KEY: str = config("IMAGEKIT_PUBLIC_KEY", default="public_71ikqJwMTi45+3s8x8ZJTmoXYv0=")
    IMAGEKIT_URL_ENDPOINT: str = config("IMAGEKIT_URL_ENDPOINT", default="https://ik.imagekit.io/3y7rfi7jj")

    # 📧 SendGrid Email Service
    SENDGRID_API_KEY: str = config("SENDGRID_API_KEY", default="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")
    SENDGRID_FROM_EMAIL: str = config("SENDGRID_FROM_EMAIL", default="alancairampoma@gmail.com")
    SENDGRID_FROM_NAME: str = config("SENDGRID_FROM_NAME", default="Casta de Gallos")
    
    # 🌐 CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # 🔄 Environment
    ENVIRONMENT: str = config("ENVIRONMENT", default="local")

settings = Settings()
