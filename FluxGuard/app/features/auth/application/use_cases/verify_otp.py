from dataclasses import dataclass
from app.features.auth.application.interfaces.services.otp_service import IOtpService
from app.features.auth.application.interfaces.services.token_service import ITokenService
from app.features.auth.application.interfaces.unit_of_work import IAuthUnitOfWork
from app.features.auth.application.dto.auth_token import AuthTokenPair
from uuid import uuid4
from app.core.domain.value_objects import UserId
from app.features.auth.domain.entities.user import User, UserRole
from app.core.application.exceptions import UnauthorizedError, ForbiddenError

@dataclass(slots=True)
class VerifyOtpCommand:
    email : str
    code : str

class VerifyOtpUseCase:
    def __init__(self,token_service : ITokenService,otp : IOtpService,uow : IAuthUnitOfWork) -> None:
        self.token_service = token_service
        self.otp = otp
        self.uow = uow
    
    async def execute(self,command : VerifyOtpCommand) -> AuthTokenPair:
        stored_code = await self.otp.get_code(command.email)
        if not stored_code or stored_code != command.code:
            raise UnauthorizedError("Invalid or expired OTP code.")
        await self.otp.delete(command.email)
        async with self.uow:
            user = await self.uow.users.get_by_email(command.email)
            if user is None:
                user = User(id=UserId(uuid4()), fullname=command.email.split("@")[0], email=command.email, role=UserRole.CLIENT, is_active=True)
                await self.uow.users.add(user)
                await self.uow.commit()
            if not user.is_active: raise ForbiddenError("User account is disabled.")

        access_token = self.token_service.create_access_token(user.id.value, user.role)
        refresh_token = self.token_service.create_refresh_token(user.id.value)
        return AuthTokenPair(access_token=access_token, refresh_token=refresh_token)