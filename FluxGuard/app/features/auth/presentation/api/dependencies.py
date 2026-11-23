from fastapi import Depends
from app.features.auth.application.interfaces.unit_of_work import IAuthUnitOfWork
from app.features.auth.application.use_cases import RefreshTokenCommand,RefreshTokenUseCase,RequestOtpUseCase,RequestOtpCommand,VerifyOtpUseCase
from app.core.infrastructure.database.database import session_factory
from app.features.auth.application.interfaces import IOtpService,ITokenService
from app.features.auth.infrastructure.database.unit_of_work import SqlAlchemyAuthUnitOfWork
from app.core.infrastructure.redis.client import redis_client
from app.features.auth.infrastructure.redis import RedisOtpService
from app.features.auth.infrastructure.security import JwtTokenService
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from app.features.auth.domain.entities.user import User
from app.core.application.exceptions import UnauthorizedError
from app.core.domain.value_objects import UserId

security = HTTPBearer(auto_error=True)

async def get_uow() -> IAuthUnitOfWork:
    return SqlAlchemyAuthUnitOfWork(session_factory=session_factory)

async def get_opt_service() -> IOtpService:
    return RedisOtpService(redis_client=redis_client)

async def get_token_service() -> ITokenService:
    return JwtTokenService()


async def get_request_otp_use_case(
    otp_service  : IOtpService = Depends(get_opt_service),
) ->RequestOtpUseCase:
    return RequestOtpUseCase(otp=otp_service)

async def get_verify_otp_use_case(
    token_service : JwtTokenService= Depends(get_token_service),
    otp_service  : RedisOtpService = Depends(get_opt_service),
    uow : SqlAlchemyAuthUnitOfWork = Depends(get_uow) 
) -> VerifyOtpUseCase:
    return VerifyOtpUseCase(token_service=token_service,otp=otp_service,uow=uow)

async def get_refresh_token_use_case(
    token_service : JwtTokenService= Depends(get_token_service),
    uow : SqlAlchemyAuthUnitOfWork = Depends(get_uow),
) -> RefreshTokenUseCase:
    return RefreshTokenUseCase(token_service=token_service,uow=uow)

async def get_current_user(
    credentials : HTTPAuthorizationCredentials = Depends(security),
    token_service : JwtTokenService = Depends(get_token_service),
    uow : SqlAlchemyAuthUnitOfWork = Depends(get_uow)
) -> User:
    token = credentials.credentials
    payload = token_service.decode_token(token)
    if payload.role is None:
        raise UnauthorizedError("Invalid access token")
    
    async with uow:
        user = await uow.users.get_by_id(UserId(payload.sub))
        if user is None or not user.is_active:
            raise UnauthorizedError("User not active or disapperead")
    
    return user

