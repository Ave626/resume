from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import LectureNotFoundError
from app.application.interfaces.content_cache import ContentCache
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities import User


@dataclass(slots=True)
class DeleteLectureCommand:
    lecture_id: UUID
    actor: User


class DeleteLectureUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        content_cache: ContentCache | None = None,
    ) -> None:
        self.uow = uow
        self.content_cache = content_cache
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: DeleteLectureCommand) -> None:
        async with self.uow:
            lecture = await self.uow.lectures.get_by_id(command.lecture_id)
            if lecture is None:
                raise LectureNotFoundError("Lecture not Found")
            section = await self.uow.sections.get_by_id(lecture.section_id)
            module = await self.uow.modules.get_by_id(section.module_id) if section is not None else None
            course_id = module.course_id if module is not None else None
            if section is not None:
                await self.course_access_service.ensure_can_manage_section(
                    command.actor, section.id
                )
                section.remove_lecture(lecture.id)
                await self.uow.sections.update(section)
            await self.uow.lectures.delete(lecture)
            await self.uow.commit()
            if self.content_cache is not None and course_id is not None:
                await self.content_cache.invalidate_course(course_id)
