from uuid import UUID
from dataclasses import dataclass
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.exceptions import CourseNotFoundError

@dataclass(slots=True)
class DeleteCourseCommand:
    course_id : UUID

class DeleteCourseUseCase:
    def __init__(self,uow : UnitOfWork):
        self.uow = uow
    async def execute(self,command : DeleteCourseCommand) -> None:
        async with self.uow:
            course = await self.uow.courses.get_by_id(command.course_id)
            if course is None:
                raise CourseNotFoundError("Course not found")
            await self.uow.courses.delete(course)
            await self.uow.commit()