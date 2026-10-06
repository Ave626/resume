from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.domain.entities.student_activity import StudentActivity, StudentActivityType
from app.infrastructure.database.models import CourseModel, UserModel
from app.infrastructure.database.repositories.student_activity_repository import (
    SqlAlchemyStudentActivityRepository,
)


@pytest.mark.asyncio
async def test_student_activity_repository_lifecycle(session_factory):
    student1_id = uuid4()
    student2_id = uuid4()
    course_id = uuid4()

    async with session_factory() as session:
        user1 = UserModel(
            id=str(student1_id),
            email="act_student1@example.com",
            hashed_password="hash",
            role="student",
        )
        user2 = UserModel(
            id=str(student2_id),
            email="act_student2@example.com",
            hashed_password="hash",
            role="student",
        )
        course = CourseModel(
            id=str(course_id),
            author_id=str(student1_id),
            title="Activity Test Course",
            description="Testing activity repository",
        )
        session.add_all([user1, user2, course])
        await session.commit()

    async with session_factory() as session:
        repo = SqlAlchemyStudentActivityRepository(session)

        now = datetime.now(UTC)
        act1 = StudentActivity(
            id=uuid4(),
            student_id=student1_id,
            course_id=course_id,
            activity_type=StudentActivityType.QUESTION_COMPLETED,
            entity_id=uuid4(),
            title="Completed Quiz 1",
            details={"score": 10},
            occurred_at=now - timedelta(minutes=10),
        )
        act2 = StudentActivity(
            id=uuid4(),
            student_id=student1_id,
            course_id=course_id,
            activity_type=StudentActivityType.TASK_COMPLETED,
            entity_id=uuid4(),
            title="Completed Task 1",
            details={"awarded": 15},
            occurred_at=now,
        )
        act3 = StudentActivity(
            id=uuid4(),
            student_id=student2_id,
            course_id=course_id,
            activity_type=StudentActivityType.SECTION_COMPLETED,
            entity_id=uuid4(),
            title="Section Done",
            details={},
            occurred_at=now,
        )

        await repo.add(act1)
        await repo.add(act2)
        await repo.add(act3)
        await session.commit()

    async with session_factory() as session:
        repo = SqlAlchemyStudentActivityRepository(session)

        count1 = await repo.count_by_student_id(student1_id)
        count2 = await repo.count_by_student_id(student2_id)
        count_none = await repo.count_by_student_id(uuid4())

        assert count1 == 2
        assert count2 == 1
        assert count_none == 0

        activities1 = await repo.list_by_student_id(student1_id, limit=10, offset=0)
        assert len(activities1) == 2
        assert activities1[0].id == act2.id
        assert activities1[0].title == "Completed Task 1"
        assert activities1[0].details == {"awarded": 15}
        assert activities1[1].id == act1.id
        assert activities1[1].title == "Completed Quiz 1"

        paginated = await repo.list_by_student_id(student1_id, limit=1, offset=1)
        assert len(paginated) == 1
        assert paginated[0].id == act1.id

        total_all = await repo.count_all()
        assert total_all == 3

        count_filtered = await repo.count_all(
            activity_type=StudentActivityType.QUESTION_COMPLETED
        )
        assert count_filtered == 1

        count_course_ids = await repo.count_all(course_ids=[course_id])
        assert count_course_ids == 3

        count_empty_course_ids = await repo.count_all(course_ids=[uuid4()])
        assert count_empty_course_ids == 0

        list_filtered = await repo.list_all(
            activity_type=StudentActivityType.TASK_COMPLETED
        )
        assert len(list_filtered) == 1
        assert list_filtered[0].id == act2.id

        list_student = await repo.list_all(student_id=student1_id)
        assert len(list_student) == 2
        assert list_student[0].id == act2.id
        assert list_student[1].id == act1.id
