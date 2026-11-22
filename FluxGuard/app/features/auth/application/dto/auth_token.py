from dataclasses import dataclass

@dataclass(slots=True)
class AuthToken:
    token : str
    token_type : str = "bearer"


@dataclass(slots=True)
class AuthTokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"