from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import (
    SectionNotFoundError,
    TaskAlreadyUsedError,
    TaskNotFoundError,
)
from app.application.interfaces.content_cache import ContentCache
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.task import Task
from app.domain.entities.user import User


@dataclass(slots=True)
class DeleteTaskCommand:
    actor: User
    task_id: UUID


class DeleteTaskUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        content_cache: ContentCache | None = None,
    ):
        self.uow = uow
        self.content_cache = content_cache
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: DeleteTaskCommand):
        async with self.uow:
            task = await self.uow.tasks.get_by_id(command.task_id)
            if task is None:
                raise TaskNotFoundError("Task not found")

            has_attempts = await self.uow.task_attempts.exists_by_task_id(task.id)
            if has_attempts:
                raise TaskAlreadyUsedError(
                    "Task already has student and cannot be deleted"
                )

            section = await self.course_access_service.ensure_can_manage_section(
                actor=command.actor, section_id=task.section_id
            )
            module = await self.uow.modules.get_by_id(section.module_id) if section is not None else None

            section.remove_task(task.id)
            await self.uow.sections.update(section)
            await self.uow.tasks.delete(task)
            await self.uow.commit()
            if self.content_cache is not None and module is not None:
                await self.content_cache.invalidate_course(module.course_id)
