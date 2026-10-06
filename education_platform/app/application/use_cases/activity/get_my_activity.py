from dataclasses import dataclass

from app.application.dto.student_activity import StudentActivityDTO
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.user import User


@dataclass(slots=True)
class GetMyActivitiesCommand:
    actor: User
    limit: int = 20
    offset: int = 0


class GetMyActivitiesUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(
        self, command: GetMyActivitiesCommand
    ) -> list[StudentActivityDTO]:
        async with self.uow:
            activities = await self.uow.student_activities.list_by_student_id(
                student_id=command.actor.id,
                limit=command.limit,
                offset=command.offset,
            )
            return [
                StudentActivityDTO(
                    id=activity.id,
                    student_id=activity.student_id,
                    course_id=activity.course_id,
                    activity_type=activity.activity_type,
                    entity_id=activity.entity_id,
                    title=activity.title,
                    details=activity.details,
                    occurred_at=activity.occurred_at,
                )
                for activity in activities
            ]
