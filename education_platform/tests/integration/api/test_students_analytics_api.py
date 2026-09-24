from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4
import pytest

from app.infrastructure.database.models import CodeSubmissionModel
from app.infrastructure.queues.redis_submission_queues import RedisSubmissionQueue


@pytest.mark.asyncio
async def test_student_analytics_returns_empty_progress_for_not_started_course(
        client,
        student_auth_headers,
        seeded_course_tree,
):
    response = await client.get(
        f'/api/profile/me/courses/{seeded_course_tree.course_id}/analytics',
        headers=student_auth_headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload['course_id'] == seeded_course_tree.course_id
    assert payload['completion_ratio'] == 0.0
    assert payload['is_completed'] is False
    assert payload['total_points'] == 0
    assert payload['completed_modules_count'] == 0
    assert payload['completed_sections_count'] == 0
    assert payload['weak_questions'] == []
    assert payload['weak_tasks'] == []
    assert payload['weak_code_tasks'] == []


@pytest.mark.asyncio
async def test_student_analytics_detects_weak_code_tasks(
    client,
    student_auth_headers,
    seeded_tasks_tree,
    monkeypatch,
):
    monkeypatch.setattr(RedisSubmissionQueue, 'enqueue', AsyncMock())
    first_submission = await client.post(
        f'/api/learning/code-tasks/{seeded_tasks_tree.code_task_id}/submissions',
        headers=student_auth_headers,
        json={'source_code': 'print("first")'},
    )
    assert first_submission.status_code == 202

    second_submission = await client.post(
        f'/api/learning/code-tasks/{seeded_tasks_tree.code_task_id}/submissions',
        headers=student_auth_headers,
        json={'source_code': 'print("second")'},
    )
    assert second_submission.status_code == 202

    response = await client.get(
        f'/api/profile/me/courses/{seeded_tasks_tree.course_id}/analytics',
        headers=student_auth_headers,
    )
    assert response.status_code == 200
    payload = response.json()
    assert len(payload['weak_code_tasks']) == 1
    assert payload['weak_code_tasks'][0]['code_task_id'] == seeded_tasks_tree.code_task_id
    assert payload['weak_code_tasks'][0]['section_id'] == seeded_tasks_tree.section_id
    assert payload['weak_code_tasks'][0]['attempts_count'] == 2


@pytest.mark.asyncio
async def test_student_analytics_detects_failed_code_submission_as_weak(
    client,
    student_auth_headers,
    seeded_tasks_tree,
    session_factory,
    seeded_student_user,
):
    async with session_factory() as session:
        submission = CodeSubmissionModel(
            id=str(uuid4()),
            code_task_id=seeded_tasks_tree.code_task_id,
            student_id=str(seeded_student_user.id),
            source_code='print(1)',
            attempt_number=1,
            status='failed',
            created_at=datetime.now(UTC),
        )
        session.add(submission)
        await session.commit()

    response = await client.get(
        f'/api/profile/me/courses/{seeded_tasks_tree.course_id}/analytics',
        headers=student_auth_headers,
    )
    assert response.status_code == 200
    payload = response.json()
    assert len(payload['weak_code_tasks']) == 1
    assert payload['weak_code_tasks'][0]['code_task_id'] == seeded_tasks_tree.code_task_id
    assert payload['weak_code_tasks'][0]['section_id'] == seeded_tasks_tree.section_id
    assert payload['weak_code_tasks'][0]['attempts_count'] == 1