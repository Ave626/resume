from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import LectureNotFoundError,SectionNotFoundError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.lecture import Lecture
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.user import User


@dataclass(slots=True)
class UpdateLectureCommand:
    lecture_id: UUID
    title: str
    content: str
    position: int
    actor : User


class UpdateLectureUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: UpdateLectureCommand) -> Lecture:
        async with self.uow:
            lecture = await self.uow.lectures.get_by_id(command.lecture_id)
            if lecture is None:
                raise LectureNotFoundError("Lecture not found")
            section = await self.uow.sections.get_by_id(lecture.section_id)
            if section is None:
                raise SectionNotFoundError("Section not found")
            await self.course_access_service.ensure_can_manage_section(command.actor,section.id)
            lecture.update(
                title=command.title, content=command.content, position=command.position
            )
            await self.uow.lectures.update(lecture)
            await self.uow.commit()
            return lecture
