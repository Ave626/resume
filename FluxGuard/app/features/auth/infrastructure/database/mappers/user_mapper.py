from app.features.auth.domain.entities.user import User,UserRole
from app.features.auth.infrastructure.database.models.user_model import UserModel

class UserMapper:
    @staticmethod
    def to_domain(model : UserModel) -> User:
        return User(
            id = model.id,
            fullname=model.fullname,
            email=model.email,
            role = UserRole(model.role),
            is_active=model.is_active,
            created_at=model.created_at
        )
    @staticmethod
    def to_model(entity : User) -> UserModel:
        return UserModel(
            id = entity.id,
            fullname=entity.fullname,
            email=entity.email,
            role=entity.role.value,
            is_active=entity.is_active,
            created_at=entity.created_at,
        )