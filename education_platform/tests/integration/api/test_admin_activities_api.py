from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest

from app.domain.entities.student_activity import StudentActivity, StudentActivityType
from app.infrastructure.database.models import CourseModel, UserModel
from app.infrastructure.database.repositories.student_activity_repository import (
    SqlAlchemyStudentActivityRepository,
)


@pytest.mark.asyncio
async def test_admin_activities_unauthorized(client):
    response = await client.get("/api/admin/activities")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_activities_forbidden_for_student(client, student_auth_headers):
    response = await client.get("/api/admin/activities", headers=student_auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_activities_full_access_and_filters(
    client,
    admin_auth_headers,
    seeded_admin_user,
    session_factory,
):
    student1_id = uuid4()
    student2_id = uuid4()
    course1_id = uuid4()
    course2_id = uuid4()
    now = datetime.now(UTC)

    async with session_factory() as session:
        u1 = UserModel(
            id=str(student1_id),
            email="s1_admin_test@example.com",
            hashed_password="hash",
            role="student",
        )
        u2 = UserModel(
            id=str(student2_id),
            email="s2_admin_test@example.com",
            hashed_password="hash",
            role="student",
        )
        c1 = CourseModel(
            id=str(course1_id),
            author_id=str(seeded_admin_user.id),
            title="Course 1",
            description="desc",
        )
        c2 = CourseModel(
            id=str(course2_id),
            author_id=str(seeded_admin_user.id),
            title="Course 2",
            description="desc",
        )
        session.add_all([u1, u2, c1, c2])
        await session.commit()

    async with session_factory() as session:
        repo = SqlAlchemyStudentActivityRepository(session)
        act1 = StudentActivity(
            id=uuid4(),
            student_id=student1_id,
            course_id=course1_id,
            activity_type=StudentActivityType.QUESTION_COMPLETED,
            entity_id=uuid4(),
            title="Question 1",
            details={"score": 5},
            occurred_at=now - timedelta(minutes=10),
        )
        act2 = StudentActivity(
            id=uuid4(),
            student_id=student1_id,
            course_id=course2_id,
            activity_type=StudentActivityType.TASK_COMPLETED,
            entity_id=uuid4(),
            title="Task 1",
            details={},
            occurred_at=now - timedelta(minutes=5),
        )
        act3 = StudentActivity(
            id=uuid4(),
            student_id=student2_id,
            course_id=course1_id,
            activity_type=StudentActivityType.SECTION_COMPLETED,
            entity_id=uuid4(),
            title="Section 1",
            details={},
            occurred_at=now,
        )
        await repo.add(act1)
        await repo.add(act2)
        await repo.add(act3)
        await session.commit()

    res_all = await client.get("/api/admin/activities", headers=admin_auth_headers)
    assert res_all.status_code == 200
    assert len(res_all.json()) >= 3

    res_student = await client.get(
        f"/api/admin/activities?student_id={student1_id}",
        headers=admin_auth_headers,
    )
    assert res_student.status_code == 200
    s_items = res_student.json()
    assert len(s_items) == 2

    res_course = await client.get(
        f"/api/admin/activities?course_id={course2_id}",
        headers=admin_auth_headers,
    )
    assert res_course.status_code == 200
    c_items = res_course.json()
    assert len(c_items) == 1
    assert c_items[0]["id"] == str(act2.id)

    res_type = await client.get(
        f"/api/admin/activities?activity_type={StudentActivityType.SECTION_COMPLETED}",
        headers=admin_auth_headers,
    )
    assert res_type.status_code == 200
    t_items = res_type.json()
    assert any(item["id"] == str(act3.id) for item in t_items)


@pytest.mark.asyncio
async def test_author_activities_scoped_to_owned_courses(
    client,
    author_auth_headers,
    seeded_author_user,
    seeded_admin_user,
    session_factory,
):
    author_id = UUID(seeded_author_user.id)
    student_id = uuid4()
    own_course_id = uuid4()
    foreign_course_id = uuid4()
    now = datetime.now(UTC)

    async with session_factory() as session:
        student = UserModel(
            id=str(student_id),
            email="s_author_test@example.com",
            hashed_password="hash",
            role="student",
        )
        c_own = CourseModel(
            id=str(own_course_id),
            author_id=str(author_id),
            title="Author Own Course",
            description="desc",
        )
        c_foreign = CourseModel(
            id=str(foreign_course_id),
            author_id=str(seeded_admin_user.id),
            title="Foreign Course",
            description="desc",
        )
        session.add_all([student, c_own, c_foreign])
        await session.commit()

    async with session_factory() as session:
        repo = SqlAlchemyStudentActivityRepository(session)
        act_own = StudentActivity(
            id=uuid4(),
            student_id=student_id,
            course_id=own_course_id,
            activity_type=StudentActivityType.COURSE_REVIEW_CREATED,
            entity_id=uuid4(),
            title="Review created",
            details={"rating": 5},
            occurred_at=now,
        )
        act_foreign = StudentActivity(
            id=uuid4(),
            student_id=student_id,
            course_id=foreign_course_id,
            activity_type=StudentActivityType.COURSE_REVIEW_CREATED,
            entity_id=uuid4(),
            title="Foreign review created",
            details={"rating": 4},
            occurred_at=now,
        )
        await repo.add(act_own)
        await repo.add(act_foreign)
        await session.commit()

    res_all_author = await client.get(
        "/api/admin/activities",
        headers=author_auth_headers,
    )
    assert res_all_author.status_code == 200
    author_items = res_all_author.json()
    assert any(i["id"] == str(act_own.id) for i in author_items)
    assert not any(i["id"] == str(act_foreign.id) for i in author_items)

    res_own_course = await client.get(
        f"/api/admin/activities?course_id={own_course_id}",
        headers=author_auth_headers,
    )
    assert res_own_course.status_code == 200
    own_items = res_own_course.json()
    assert len(own_items) == 1
    assert own_items[0]["id"] == str(act_own.id)

    res_foreign_course = await client.get(
        f"/api/admin/activities?course_id={foreign_course_id}",
        headers=author_auth_headers,
    )
    assert res_foreign_course.status_code == 403
