from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.domain.entities.student_activity import StudentActivityType


class StudentActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    student_id: UUID
    course_id: UUID
    activity_type: StudentActivityType
    entity_id: UUID
    title: str
    details: dict[str, Any]
    occurred_at: datetime