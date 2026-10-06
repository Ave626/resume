from dataclasses import dataclass
from uuid import UUID

from app.application.dto.student_activity import StudentActivityDTO
from app.application.exceptions import PermissionDeniedError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.student_activity import StudentActivityType
from app.domain.entities.user import User


@dataclass(slots=True)
class GetAdminActivitiesCommand:
    actor: User
    student_id: UUID | None = None
    course_id: UUID | None = None
    activity_type: StudentActivityType | None = None
    limit: int = 20
    offset: int = 0


class GetAdminActivitiesUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(
        self, command: GetAdminActivitiesCommand
    ) -> list[StudentActivityDTO]:
        if not (command.actor.is_admin() or command.actor.is_author()):
            raise PermissionDeniedError("Only admins and authors can view activities.")

        course_ids: list[UUID] | None = None

        async with self.uow:
            if command.actor.is_author():
                courses = await self.uow.courses.list()
                owned_course_ids = [
                    c.id for c in courses if c.is_owned_by(command.actor.id)
                ]

                if command.course_id is not None:
                    if command.course_id not in owned_course_ids:
                        raise PermissionDeniedError(
                            "Cannot view activities of foreign course."
                        )
                else:
                    if not owned_course_ids:
                        return []
                    course_ids = owned_course_ids

            activities = await self.uow.student_activities.list_all(
                student_id=command.student_id,
                course_id=command.course_id,
                activity_type=command.activity_type,
                course_ids=course_ids,
                limit=command.limit,
                offset=command.offset,
            )
            return [
                StudentActivityDTO(
                    id=item.id,
                    student_id=item.student_id,
                    course_id=item.course_id,
                    activity_type=item.activity_type,
                    entity_id=item.entity_id,
                    title=item.title,
                    details=item.details,
                    occurred_at=item.occurred_at,
                )
                for item in activities
            ]
