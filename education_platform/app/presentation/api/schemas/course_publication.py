from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CoursePublicationIssueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    message: str
    entity_id: UUID | None = None


class CoursePublicationReadinessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    course_id: UUID
    is_ready: bool
    issues: list[CoursePublicationIssueResponse]


class CoursePublicationErrorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    error: str
    message: str
    issues: list[CoursePublicationIssueResponse]
