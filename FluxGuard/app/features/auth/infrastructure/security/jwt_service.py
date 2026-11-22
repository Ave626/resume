from app.features.auth.application.interfaces.services.token_service import ITokenService
from app.core.infrastructure.config.settings import settings
from datetime import datetime,timedelta,timezone,UTC
import jwt
from uuid import UUID
from app.features.auth.domain.entities.user import UserRole
from app.features.auth.application.dto.token_payload import TokenPayload
from app.core.application.exceptions import UnauthorizedError

class JwtTokenService(ITokenService):
    def __init__(self) -> None:
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_expire = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_expire = settings.REFRESH_TOKEN_EXPIRE_DAYS

    def create_access_token(self,user_id : UUID,role : UserRole) -> str:
        exp = datetime.now(tz=UTC) + timedelta(minutes=self.access_expire)
        payload = {
            "sub" : str(user_id),
            "role" : role.value,
            "exp" : exp,
            "type" : "access"
        }
        return jwt.encode(payload=payload,key=self.secret_key,algorithm=self.algorithm)
    

    def create_refresh_token(self,user_id : UUID) -> str:
        exp = datetime.now(tz=UTC) + timedelta(days=self.refresh_expire)
        payload = {
            "sub" : str(user_id),
            "exp" : exp,
            "type" : "refresh"
        }
        return jwt.encode(payload=payload,key=self.secret_key,algorithm=self.algorithm)
    
    def decode_token(self,token : str) -> TokenPayload:
        try:
            payload = jwt.decode(token,self.secret_key,algorithms=[self.algorithm])
        except jwt.PyJWTError:
            raise UnauthorizedError("Token is invalid or expired.")
        subject = payload.get("sub")
        if subject is None:
            raise UnauthorizedError("Token doenst have sub")
        role_raw = payload.get("role")
        role = UserRole(role_raw) if role_raw else None

        return TokenPayload(sub=UUID(subject), role=role, exp=payload["exp"])