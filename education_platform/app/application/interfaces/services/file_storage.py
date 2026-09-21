from abc import ABC,abstractmethod

class FileStorage(ABC):
    @abstractmethod
    async def upload(
        self,
        file_name : str,
        content : bytes,
        content_type : str
    ) -> str:
        raise NotImplementedError