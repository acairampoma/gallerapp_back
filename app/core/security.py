from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.config import settings
from app.database import get_db

# 🔐 Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 🔑 JWT Bearer scheme
security = HTTPBearer()

class SecurityService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verificar password con hash - protegido contra ataques"""
        try:
            # 🛡️ PROTECCIÓN: SOLO truncar si es realmente muy larga (>70 bytes)
            password_bytes = len(plain_password.encode('utf-8'))
            if password_bytes > 70:  # Solo truncar passwords anormalmente largas
                plain_password = plain_password.encode('utf-8')[:70].decode('utf-8', errors='ignore')
                print(f"🚨 SECURITY: Password truncated from {password_bytes} to 70 bytes")

            return pwd_context.verify(plain_password, hashed_password)
        except ValueError as e:
            # Capturar específicamente errores de bcrypt por passwords largas
            if "password cannot be longer than 72 bytes" in str(e):
                print(f"🚨 SECURITY: bcrypt ValueError caught, password length: {len(plain_password.encode('utf-8'))}")
                return False  # Deny access para passwords maliciosas
            # Re-raise otros errores de ValueError
            raise e
        except Exception as e:
            # Capturar cualquier otro error relacionado con bcrypt
            print(f"🚨 SECURITY ERROR: bcrypt verification failed: {str(e)}")
            return False

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generar hash de password - protegido contra ataques"""
        try:
            # 🛡️ PROTECCIÓN: Truncar contraseña a 72 bytes para evitar crashes
            if len(password.encode('utf-8')) > 72:
                password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
            return pwd_context.hash(password)
        except ValueError as e:
            # Capturar específicamente errores de bcrypt por passwords largas
            if "password cannot be longer than 72 bytes" in str(e):
                # Si aún falla, truncar más agresivamente
                password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
                try:
                    return pwd_context.hash(password)
                except:
                    # Si aún falla, generar un hash seguro por defecto
                    raise HTTPException(status_code=400, detail="Password format not supported")
            # Re-raise otros errores de ValueError
            raise e
        except Exception as e:
            # Capturar cualquier otro error relacionado con bcrypt
            print(f"🚨 SECURITY ERROR: bcrypt hashing failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Password hashing failed")
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Crear JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Crear JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> dict:
        """Verificar y decodificar JWT token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            
            # Verificar tipo de token
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            # Verificar expiración
            exp = payload.get("exp")
            if exp is None or datetime.utcnow() > datetime.utcfromtimestamp(exp):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired"
                )
            
            return payload
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

# 🔒 Dependency para obtener usuario actual desde token
async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Obtener ID del usuario actual desde JWT token"""
    token = credentials.credentials
    payload = SecurityService.verify_token(token)
    user_id: int = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    return user_id

# 🛡️ Dependency para verificar token válido
async def verify_token_dependency(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verificar que el token sea válido"""
    token = credentials.credentials
    return SecurityService.verify_token(token)

# 👤 Dependency para obtener usuario completo desde token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Obtener objeto User completo desde JWT token"""
    from app.models.user import User  # Import local para evitar circular imports
    
    token = credentials.credentials
    payload = SecurityService.verify_token(token)
    user_id: int = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    # Buscar usuario en BD
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user
