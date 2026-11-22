from abc import ABC,abstractmethod
from uuid import UUID
from app.features.auth.domain.entities.user import User,UserRole
from app.features.auth.application.dto.token_payload import TokenPayload

class ITokenService(ABC):
    @abstractmethod
    def create_access_token(self,user_id : UUID,role : UserRole) -> str:
        raise NotImplementedError
    
    @abstractmethod
    def create_refresh_token(self,user_id : UUID) -> str:
        raise NotImplementedError
    
    @abstractmethod
    def decode_token(self,token : str) -> TokenPayload:
        raise NotImplementedError