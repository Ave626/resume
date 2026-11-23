from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.features.auth.domain.entities.user import UserRole


class RequestCode(BaseModel):
    email: EmailStr


class SubmitCode(RequestCode):
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class MeResponse(BaseModel):
    id: UUID
    email: EmailStr
    fullname: str
    role: UserRole
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    model_config = ConfigDict(from_attributes=True)


class StatusMessageResponse(BaseModel):
    message: str = "Verification code sent to email."
