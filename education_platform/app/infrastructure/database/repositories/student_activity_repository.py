from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.repositories.student_activity_repository import (
    StudentActivityRepository,
)
from app.domain.entities.student_activity import StudentActivity, StudentActivityType
from app.infrastructure.database.mappers.student_activity_mapper import (
    StudentActivityMapper,
)
from app.infrastructure.database.models.student_activity_model import (
    StudentActivityModel,
)


class SqlAlchemyStudentActivityRepository(StudentActivityRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, activity: StudentActivity) -> None:
        self.session.add(StudentActivityMapper.to_model(activity))
        await self.session.flush()

    async def list_by_student_id(
        self,
        student_id: UUID,
        limit: int,
        offset: int,
    ) -> list[StudentActivity]:
        stmt = (
            select(StudentActivityModel)
            .where(StudentActivityModel.student_id == str(student_id))
            .order_by(
                StudentActivityModel.occurred_at.desc(),
                StudentActivityModel.id.desc(),
            )
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return [
            StudentActivityMapper.to_domain(model) for model in result.scalars().all()
        ]

    async def count_by_student_id(self, student_id: UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(StudentActivityModel)
            .where(StudentActivityModel.student_id == str(student_id))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()
    
    async def list_all(
        self,
        student_id: UUID | None = None,
        course_id: UUID | None = None,
        activity_type: StudentActivityType | None = None,
        course_ids: list[UUID] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[StudentActivity]:
        stmt = (
            select(StudentActivityModel)
        )
        if student_id is not None:
            stmt = stmt.where(StudentActivityModel.student_id == str(student_id))
        if course_id is not None:
            stmt = stmt.where(StudentActivityModel.course_id == str(course_id))
        if activity_type is not None:
            stmt = stmt.where(StudentActivityModel.activity_type == str(activity_type))
        if course_ids is not None:
            stmt = stmt.where(StudentActivityModel.course_id.in_([str(cid) for cid in course_ids]))
        
        stmt = (
            stmt.order_by(
                StudentActivityModel.occurred_at.desc(),
                StudentActivityModel.id.desc(),
            ).limit(limit).offset(offset)
        )
        result = await self.session.execute(stmt)
        return [
            StudentActivityMapper.to_domain(model) for model in result.scalars().all()
        ]
    
    async def count_all(
        self,
        student_id: UUID | None = None,
        course_id: UUID | None = None,
        activity_type: StudentActivityType | None = None,
        course_ids: list[UUID] | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(StudentActivityModel)

        if student_id is not None:
            stmt = stmt.where(StudentActivityModel.student_id == str(student_id))
        if course_id is not None:
            stmt = stmt.where(StudentActivityModel.course_id == str(course_id))
        if activity_type is not None:
            stmt = stmt.where(StudentActivityModel.activity_type == str(activity_type.value if hasattr(activity_type, "value") else activity_type))
        if course_ids is not None:
            stmt = stmt.where(StudentActivityModel.course_id.in_([str(cid) for cid in course_ids]))

        result = await self.session.execute(stmt)
        return result.scalar_one()
