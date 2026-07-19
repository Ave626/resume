from uuid import UUID
from dataclasses import dataclass
from app.application.exceptions import LectureNotFoundError
from app.application.interfaces.unit_of_work import UnitOfWork


@dataclass(slots=True)
class DeleteLectureCommand:
    lecture_id: UUID


class DeleteLectureUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, command: DeleteLectureCommand) -> None:
        async with self.uow:
            lecture = await self.uow.lectures.get_by_id(command.lecture_id)
            if lecture is None:
                raise LectureNotFoundError("Lecture not Found")
            section = await self.uow.sections.get_by_id(lecture.section_id)
            if section is not None:
                section.remove_lecture(lecture.id)
                await self.uow.sections.update(section)
            await self.uow.lectures.delete(lecture)
            await self.uow.commit()
