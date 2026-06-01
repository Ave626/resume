from app.domain.exceptions import InvalidUserError
from dataclasses import dataclass
from uuid import UUID
from enum import StrEnum

class UserRole(StrEnum):
    STUDENT = "student"
    AUTHOR = "author"
    ADMIN = "admin"

@dataclass(slots = True)
class User:
    id : UUID
    email : str
    hashed_password : str
    role : UserRole
    
    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        if not self.email or "@" not in self.email:
            raise InvalidUserError("Некорректный адрес электронной почты")
        if not self.hashed_password or not self.hashed_password.strip():
            raise InvalidUserError("Хешированный пароль не может быть пустым")
    
    def is_admin(self) -> bool:
        return self.role is UserRole.ADMIN
    
    def is_author(self) -> bool:
        return self.role is UserRole.AUTHOR
    
    def is_student(self) -> bool:
        return self.role is UserRole.STUDENT
    
    def can_manage_platform(self) -> bool:
        return self.is_admin()
    
    def can_take_learning_activities(self) -> bool:
        return self.is_student()

    def can_manage_content(self) -> bool:
        return self.can_manage_platform()
