from abc import abstractmethod,ABC
from uuid import UUID
from app.features.auth.domain.entities.user import User

class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self,user_id) -> User | None:
        raise NotImplementedError
    
    @abstractmethod
    async def add(self,user : User) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def delete(self,user : User) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def get_by_email(self,email : str) -> User | None:
        raise NotImplementedError