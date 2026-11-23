from dataclasses import dataclass
from app.core.application import ForbiddenError, UnauthorizedError
from app.core.domain import UserId
from app.features.auth.application.dto import AuthTokenPair
from app.features.auth.application.interfaces import (
    IAuthUnitOfWork,
    ITokenService,
)


@dataclass(slots=True)
class RefreshTokenCommand:
    refresh_token: str


class RefreshTokenUseCase:
    def __init__(
        self, token_service: ITokenService, uow: IAuthUnitOfWork
    ) -> None:
        self.token_service = token_service
        self.uow = uow

    async def execute(self, command: RefreshTokenCommand) -> AuthTokenPair:
        payload = self.token_service.decode_token(command.refresh_token)
        async with self.uow:
            user = await self.uow.users.get_by_id(UserId(payload.sub))
            if user is None:
                raise UnauthorizedError("User not found.")
            if not user.is_active:
                raise ForbiddenError("User account is disabled.")

        access_token = self.token_service.create_access_token(
            user.id.value, user.role
        )
        refresh_token = self.token_service.create_refresh_token(user.id.value)
        return AuthTokenPair(
            access_token=access_token, refresh_token=refresh_token
        )
