from dataclasses import dataclass
from app.core.domain.base import ValueObject
from app.core.domain.exceptions import InvalidValueObjectError
import ipaddress
from typing import NewType
from uuid import UUID

UserId = NewType("UserId", UUID)
ProjectId = NewType("ProjectId", UUID)
RuleId = NewType("RuleId", UUID)
IncidentId = NewType("IncidentId", UUID)

@dataclass(slots=True,frozen=True)
class IpAddress(ValueObject):
    value : str
    
    def __post_init__(self) -> None:
        self._validate()
    
    def _validate(self) -> None:
        try:
            parsed = ipaddress.ip_address(self.value)
            object.__setattr__(self, "value", str(parsed))
        except ValueError:
            raise InvalidValueObjectError(f"Invalid IP address: {self.value}")
        
    def __str__(self):
        return f"{self.value}"

