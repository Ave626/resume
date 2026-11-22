from dataclasses import dataclass,field
from uuid import UUID
from enum import Enum
from app.core.domain.exceptions import InvalidValueObjectError
from app.core.domain.base import Entity
from app.core.domain.value_objects import UserId
from datetime import datetime,timezone

class UserRole(Enum):
    ADMIN = "admin"
    CLIENT = "client"

@dataclass(kw_only=True)
class User(Entity[UserId]):
    fullname : str
    email : str
    role : UserRole = UserRole.CLIENT
    is_active : bool
    created_at : datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    
    def __post_init__(self) -> None:
        self._validate()
    
    def _validate(self) -> None:
        if not self.fullname.strip():
            raise InvalidValueObjectError("Поля не должно быть пустым")
    
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN
    
    def update(self,fullname : str,email : str, is_active : bool) -> None:
        self.fullname = fullname
        self.email = email
        self.is_active = is_active        
    
    
        