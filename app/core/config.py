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
    IMAGEKIT_PRIVATE_KEY: str = config("IMAGEKIT_PRIVATE_KEY", default="private_juJdHhsZIjOMwacjNq6/94YqfYo=")
    IMAGEKIT_PUBLIC_KEY: str = config("IMAGEKIT_PUBLIC_KEY", default="public_m7rawfzMCD/O2+1pNfMA8aHqCkk=")
    IMAGEKIT_URL_ENDPOINT: str = config("IMAGEKIT_URL_ENDPOINT", default="https://ik.imagekit.io/3y7rfi7jj")

    # 📧 SendGrid Email Service (Anterior - será reemplazado)
    SENDGRID_API_KEY: str = config("SENDGRID_API_KEY", default="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")
    SENDGRID_FROM_EMAIL: str = config("SENDGRID_FROM_EMAIL", default="alancairampoma@gmail.com")
    SENDGRID_FROM_NAME: str = config("SENDGRID_FROM_NAME", default="Casta de Gallos")
    
    # 📧 SMTP Email Service (Nuevo - servidor propio)
    SMTP_HOST: str = config("SMTP_HOST", default="mail.jsinnovatech.com")
    SMTP_PORT: int = config("SMTP_PORT", default=587, cast=int)
    SMTP_USER: str = config("SMTP_USER", default="sistemas@jsinnovatech.com")
    SMTP_PASSWORD: str = config("SMTP_PASSWORD", default="Joa420188*")
    SMTP_FROM_EMAIL: str = config("SMTP_FROM_EMAIL", default="sistemas@jsinnovatech.com")
    SMTP_FROM_NAME: str = config("SMTP_FROM_NAME", default="Sistemas Gallistico")
    USE_SMTP: bool = config("USE_SMTP", default=True, cast=bool)
    
    # 🌐 CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # 🔄 Environment
    ENVIRONMENT: str = config("ENVIRONMENT", default="local")

settings = Settings()
