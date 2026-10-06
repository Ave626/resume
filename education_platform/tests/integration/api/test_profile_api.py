from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest

from app.domain.entities.student_activity import StudentActivity, StudentActivityType
from app.infrastructure.database.models import CourseModel
from app.infrastructure.database.repositories.student_activity_repository import (
    SqlAlchemyStudentActivityRepository,
)


@pytest.mark.asyncio
async def test_get_my_profile_returns_authenticated_user_profile(
    client,
    student_auth_headers,
):
    response = await client.get("/api/profile/me", headers=student_auth_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["email"] == "student@example.com"
    assert payload["role"] == "student"
    assert payload["full_name"] == ""
    assert payload["bio"] == ""
    assert payload["avatar_url"] is None


@pytest.mark.asyncio
async def test_update_my_profile_changes_profile_fields(
    client,
    student_auth_headers,
):
    response = await client.patch(
        "/api/profile/me",
        headers=student_auth_headers,
        json={
            "full_name": "Ivan Petrov",
            "bio": "Learning backend development.",
            "avatar_url": "https://example.com/avatars/ivan.png",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["full_name"] == "Ivan Petrov"
    assert payload["bio"] == "Learning backend development."
    assert payload["avatar_url"] == "https://example.com/avatars/ivan.png"


@pytest.mark.asyncio
async def test_get_my_profile_returns_updated_profile_data(
    client,
    student_auth_headers,
):
    await client.patch(
        "/api/profile/me",
        headers=student_auth_headers,
        json={
            "full_name": "Ivan Petrov",
            "bio": "Learning backend development.",
            "avatar_url": "https://example.com/avatars/ivan.png",
        },
    )

    response = await client.get("/api/profile/me", headers=student_auth_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["full_name"] == "Ivan Petrov"
    assert payload["bio"] == "Learning backend development."
    assert payload["avatar_url"] == "https://example.com/avatars/ivan.png"


@pytest.mark.asyncio
async def test_author_teaching_analytics_returns_course_metrics(
    client,
    author_auth_headers,
    seeded_tasks_tree,
):
    response = await client.get(
        f"/api/profile/me/teaching/courses/{seeded_tasks_tree.course_id}/analytics",
        headers=author_auth_headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["course_id"] == seeded_tasks_tree.course_id
    assert payload["course_title"] == "Tasks course"
    assert payload["students_started_count"] == 0
    assert payload["students_completed_count"] == 0
    assert payload["completion_rate"] == 0.0
    assert payload["average_completion_ratio"] == 0.0
    assert payload["average_points"] == 0.0
    assert len(payload["modules"]) == 1
    assert payload["difficult_questions"] == []
    assert payload["difficult_tasks"] == []
    assert payload["problematic_code_tasks"] == []


@pytest.mark.asyncio
async def test_author_teaching_analytics_forbidden_for_student(
    client,
    student_auth_headers,
    seeded_tasks_tree,
):
    response = await client.get(
        f"/api/profile/me/teaching/courses/{seeded_tasks_tree.course_id}/analytics",
        headers=student_auth_headers,
    )

    assert response.status_code == 403
    assert response.json()["error"] == "permission_denied"


@pytest.mark.asyncio
async def test_get_my_activities_unauthorized(client):
    response = await client.get("/api/profile/me/activities")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_my_activities_returns_own_ordered_and_paginated(
    client,
    student_auth_headers,
    seeded_student_user,
    seeded_admin_user,
    session_factory,
):
    course_id = uuid4()
    now = datetime.now(UTC)

    async with session_factory() as session:
        course = CourseModel(
            id=str(course_id),
            author_id=str(seeded_admin_user.id),
            title="Course For Activities",
            description="Course desc",
        )
        session.add(course)
        await session.commit()

    async with session_factory() as session:
        repo = SqlAlchemyStudentActivityRepository(session)
        act1 = StudentActivity(
            id=uuid4(),
            student_id=UUID(seeded_student_user.id),
            course_id=course_id,
            activity_type=StudentActivityType.QUESTION_COMPLETED,
            entity_id=uuid4(),
            title="Completed Question 1",
            details={"score": 10},
            occurred_at=now - timedelta(minutes=5),
        )
        act2 = StudentActivity(
            id=uuid4(),
            student_id=UUID(seeded_student_user.id),
            course_id=course_id,
            activity_type=StudentActivityType.TASK_COMPLETED,
            entity_id=uuid4(),
            title="Completed Task 1",
            details={"awarded": 15},
            occurred_at=now,
        )
        other_act = StudentActivity(
            id=uuid4(),
            student_id=UUID(seeded_admin_user.id),
            course_id=course_id,
            activity_type=StudentActivityType.SECTION_COMPLETED,
            entity_id=uuid4(),
            title="Other user activity",
            details={},
            occurred_at=now,
        )
        await repo.add(act1)
        await repo.add(act2)
        await repo.add(other_act)
        await session.commit()

    response = await client.get(
        "/api/profile/me/activities?limit=10&offset=0",
        headers=student_auth_headers,
    )
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 2
    assert items[0]["id"] == str(act2.id)
    assert items[0]["title"] == "Completed Task 1"
    assert items[1]["id"] == str(act1.id)
    assert items[1]["title"] == "Completed Question 1"

    paginated = await client.get(
        "/api/profile/me/activities?limit=1&offset=1",
        headers=student_auth_headers,
    )
    assert paginated.status_code == 200
    p_items = paginated.json()
    assert len(p_items) == 1
    assert p_items[0]["id"] == str(act1.id)
