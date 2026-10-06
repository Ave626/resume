from dataclasses import dataclass,field
from uuid import UUID
from app.domain.entities.student_activity import StudentActivityType
from typing import Any
from datetime import datetime

@dataclass(slots=True)
class StudentActivityDTO:
    id : UUID
    student_id : UUID
    course_id : UUID
    activity_type : StudentActivityType
    entity_id : UUID
    title : str
    details : dict[str,Any] = field(default_factory=dict)
    occurred_at: datetime = field(default_factory=datetime.utcnow)