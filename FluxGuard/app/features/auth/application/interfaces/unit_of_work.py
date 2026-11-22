from app.core.application.interfaces.unit_of_work import IUnitOfWork
from app.features.auth.application.interfaces.repositories.user_repository import UserRepository

class IAuthUnitOfWork(IUnitOfWork):
    users : UserRepository