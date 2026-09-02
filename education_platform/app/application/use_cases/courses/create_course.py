from dataclasses import dataclass
from uuid import uuid4

from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities import Course, User
from app.application.services.course_access_service import (
    CourseAccessService,
)
from app.application.exceptions import PermissionDeniedError


@dataclass(slots=True)
class CreateCourseCommand:
    actor: User
    title: str
    description: str


class CreateCourseUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: CreateCourseCommand) -> Course:
        async with self.uow:
            course = Course(
                id=uuid4(),
                author_id=command.actor.id,
                title=command.title,
                description=command.description,
            )
            if not command.actor.can_manage_course_structure():
                raise PermissionDeniedError("User cannot manage it")
            await self.uow.courses.add(course)
            await self.uow.commit()
            return course
