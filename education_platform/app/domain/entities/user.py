from app.domain.exceptions import InvalidUserError
from dataclasses import dataclass
from uuid import UUID

@dataclass(slots = True)
class User:
    id : UUID
    email : str
    hashed_password : str
    role : str
    
    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        if not self.email or "@" not in self.email:
            raise InvalidUserError("Некорректный адрес электронной почты")
        if not self.hashed_password or not self.hashed_password.strip():
            raise InvalidUserError("Хешированный пароль не может быть пустым")
    
