from dataclasses import dataclass
from uuid import UUID, uuid4

from app.application.exceptions import CourseNotFoundError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.module import Module
from app.application.interfaces.services.course_access_service import CourseAccessService
from app.domain.entities.user import User


@dataclass(slots=True)
class CreateModuleCommand:
    course_id: UUID
    title: str
    description: str
    position: int
    actor : User


class CreateModuleUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: CreateModuleCommand) -> Module:
        async with self.uow:
            course = await self.uow.courses.get_by_id(command.course_id)
            if course is None:
                raise CourseNotFoundError("Такого курса нет")
            module = Module(
                id=uuid4(),
                course_id=course.id,
                title=command.title,
                description=command.description,
                position=command.position,
            )
            await self.course_access_service.ensure_can_manage_course(command.actor,course.id)
            course.module_ids.append(module.id)
            await self.uow.modules.add(module)
            await self.uow.courses.update(course)
            await self.uow.commit()
            return module
