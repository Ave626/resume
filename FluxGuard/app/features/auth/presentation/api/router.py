from fastapi import APIRouter,status,Depends
from app.features.auth.presentation.api.dependencies import (
    get_current_user,
    get_opt_service,
    get_refresh_token_use_case,
    get_request_otp_use_case,
    get_token_service,
    get_uow,
    get_verify_otp_use_case
)
from app.features.auth.application.use_cases import RefreshTokenCommand,RefreshTokenUseCase,RequestOtpUseCase,RequestOtpCommand,VerifyOtpUseCase,VerifyOtpCommand
from app.features.auth.presentation.api.schemas import (
    RefreshTokenRequest,
    RequestCode,
    SubmitCode,
    TokenPairResponse,
    MeResponse,
    StatusMessageResponse
)
from app.features.auth.domain.entities.user import User

router = APIRouter(prefix="/auth")

@router.get("/me",status_code=status.HTTP_200_OK)
async def get_me(
    current_user  : User = Depends(get_current_user)
) -> MeResponse:
    return MeResponse.model_validate(current_user)


@router.post("/request-code",status_code=status.HTTP_200_OK)
async def request_code(
    body : RequestCode,
    use_case : RequestOtpUseCase = Depends(get_request_otp_use_case)
) ->  StatusMessageResponse:
    await use_case.execute(RequestOtpCommand(email=body.email))
    return StatusMessageResponse()

@router.post("/verify",status_code=status.HTTP_201_CREATED)
async def verify(
    submit : SubmitCode,
    use_case : VerifyOtpUseCase = Depends(get_verify_otp_use_case)
) -> TokenPairResponse:
    response = await use_case.execute(VerifyOtpCommand(email=submit.email,code=submit.code))
    return TokenPairResponse.model_validate(response)


@router.post("/refresh",status_code=status.HTTP_201_CREATED)
async def refresh(
    body : RefreshTokenRequest,
    use_case : RefreshTokenUseCase = Depends(get_refresh_token_use_case)
) -> TokenPairResponse:
    response = await use_case.execute(RefreshTokenCommand(refresh_token=body.refresh_token))
    return TokenPairResponse.model_validate(response)