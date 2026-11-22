from abc import ABC,abstractmethod

class IOtpService(ABC):
    @abstractmethod
    async def save(self,email : str,code : str,ex : int) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def get_code(self,email : str) -> str | None:
        raise NotImplementedError
    
    @abstractmethod
    async def delete(self,email : str) -> None:
        raise NotImplementedError