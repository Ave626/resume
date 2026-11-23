from dataclasses import dataclass
from uuid import uuid4
from app.core.application import ForbiddenError, UnauthorizedError
from app.core.domain import UserId
from app.features.auth.application.dto import AuthTokenPair
from app.features.auth.application.interfaces import (
    IAuthUnitOfWork,
    IOtpService,
    ITokenService,
)
from app.features.auth.domain import User, UserRole


@dataclass(slots=True)
class VerifyOtpCommand:
    email: str
    code: str


class VerifyOtpUseCase:
    def __init__(
        self,
        token_service: ITokenService,
        otp: IOtpService,
        uow: IAuthUnitOfWork,
    ) -> None:
        self.token_service = token_service
        self.otp = otp
        self.uow = uow

    async def execute(self, command: VerifyOtpCommand) -> AuthTokenPair:
        stored_code = await self.otp.get_code(command.email)
        if not stored_code or stored_code != command.code:
            raise UnauthorizedError("Invalid or expired OTP code.")
        await self.otp.delete(command.email)
        async with self.uow:
            user = await self.uow.users.get_by_email(command.email)
            if user is None:
                user = User(
                    id=UserId(uuid4()),
                    fullname=command.email.split("@")[0],
                    email=command.email,
                    role=UserRole.CLIENT,
                    is_active=True,
                )
                await self.uow.users.add(user)
                await self.uow.commit()
            if not user.is_active:
                raise ForbiddenError("User account is disabled.")

        access_token = self.token_service.create_access_token(
            user.id.value, user.role
        )
        refresh_token = self.token_service.create_refresh_token(user.id.value)
        return AuthTokenPair(
            access_token=access_token, refresh_token=refresh_token
        )
