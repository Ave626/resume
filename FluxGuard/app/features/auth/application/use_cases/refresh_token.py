from dataclasses import dataclass
from uuid import UUID
from app.features.auth.domain.entities.user import User
from app.features.auth.application.interfaces.unit_of_work import IAuthUnitOfWork
from app.features.auth.application.interfaces.services.token_service import ITokenService
from app.features.auth.application.dto.auth_token import AuthTokenPair
from app.core.domain.value_objects import UserId
from app.core.application.exceptions import UnauthorizedError, ForbiddenError

@dataclass(slots=True)
class RefreshTokenCommand:
     refresh_token : str
    

class RefreshTokenUseCase:
    def __init__(self,token_service : ITokenService,uow : IAuthUnitOfWork) -> None:
        self.token_service = token_service
        self.uow = uow
    
    async def execute(self,command : RefreshTokenCommand) -> AuthTokenPair:
        payload = self.token_service.decode_token(command.refresh_token)
        user_id = payload.sub
        async with self.uow:
            user = await self.uow.users.get_by_id(UserId(payload.sub))
            if user is None:
                raise UnauthorizedError("User not found.")
            if not user.is_active:
                raise ForbiddenError("User account is disabled.")
            
        access_token = self.token_service.create_access_token(user.id.value,user.role)
        refresh_token = self.token_service.create_refresh_token(user.id.value)
        return AuthTokenPair(access_token=access_token,refresh_token=refresh_token)
                

        