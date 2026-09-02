from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import CourseNotFoundError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.user import User


@dataclass(slots=True)
class DeleteCourseCommand:
    course_id: UUID
    actor : User


class DeleteCourseUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: DeleteCourseCommand) -> None:
        async with self.uow:
            course = await self.uow.courses.get_by_id(command.course_id)
            if course is None:
                raise CourseNotFoundError("Course not found")
            await self.course_access_service.ensure_can_manage_course(command.actor,course.id)
            await self.uow.courses.delete(course)
            await self.uow.commit()
