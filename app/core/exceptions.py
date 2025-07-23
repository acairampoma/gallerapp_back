from fastapi import HTTPException, status

class CustomException(HTTPException):
    """Excepción personalizada base"""
    def __init__(self, status_code: int, message: str, detail: str = None, error_code: str = None):
        self.status_code = status_code
        self.message = message
        self.detail = detail
        self.error_code = error_code
        super().__init__(status_code=status_code, detail=message)

class AuthenticationException(CustomException):
    """Excepciones de autenticación"""
    def __init__(self, message: str = "Authentication failed", detail: str = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            detail=detail,
            error_code="AUTH_ERROR"
        )

class AuthorizationException(CustomException):
    """Excepciones de autorización"""
    def __init__(self, message: str = "Access denied", detail: str = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message,
            detail=detail,
            error_code="ACCESS_DENIED"
        )

class ValidationException(CustomException):
    """Excepciones de validación"""
    def __init__(self, message: str = "Validation error", detail: str = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message,
            detail=detail,
            error_code="VALIDATION_ERROR"
        )

class NotFoundException(CustomException):
    """Excepciones de no encontrado"""
    def __init__(self, message: str = "Resource not found", detail: str = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message,
            detail=detail,
            error_code="NOT_FOUND"
        )
