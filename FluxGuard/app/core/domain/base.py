from dataclasses import dataclass,field
from uuid import UUID,uuid4
from typing import Any,Generic,TypeVar
from abc import ABC
from datetime import datetime,timezone

EntiryId = TypeVar("EntityId",bound=Any)

@dataclass(kw_only=True)
class Entity(ABC,Generic[EntiryId]):
    id : EntiryId
    _events : list[Any] = field(default_factory=list,init=False,repr=False)

    def record_event(self,event : Any) -> None:
        self._events.append(event)

    def pull_events(self) -> list[Any]:
        events = self._events.copy()
        self._events.clear()
        return events

    def __eq__(self,other : object) -> bool:
        if not isinstance(other,self.__class__):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash((self.__class__,self.id))



@dataclass(frozen=True,slots=True)
class ValueObject(ABC):
    pass

@dataclass(frozen=True,slots=True,kw_only=True)
class DomainEvent(ABC):
    event_id : UUID  = field(default_factory=uuid4)
    occured_at : datetime = field(default_factory=lambda: datetime.now(timezone.utc))