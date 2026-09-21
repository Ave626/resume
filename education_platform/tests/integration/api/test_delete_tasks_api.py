from unittest.mock import AsyncMock

import pytest

from app.infrastructure.database.models.test_case_model import TestCaseModel
from app.infrastructure.queues.redis_submission_queues import RedisSubmissionQueue

TestCaseModel.__test__ = False


@pytest.mark.asyncio
async def test_author_can_delete_task_and_it_disappears_from_structure(
    client,
    author_auth_headers,
    seeded_tasks_tree,
):
    response = await client.delete(
        f'/api/admin/tasks/{seeded_tasks_tree.task_id}',
        headers=author_auth_headers,
    )
    assert response.status_code == 204

    structure_response = await client.get(
        f'/api/courses/{seeded_tasks_tree.course_id}/structure'
    )
    assert structure_response.status_code == 200
    section = structure_response.json()['modules'][0]['sections'][0]
    assert seeded_tasks_tree.task_id not in section['task_ids']
    assert all(item['id'] != seeded_tasks_tree.task_id for item in section['tasks'])

    get_response = await client.get(f'/api/tasks/{seeded_tasks_tree.task_id}')
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_author_can_delete_code_task_and_it_disappears_from_structure(
    client,
    author_auth_headers,
    seeded_tasks_tree,
):
    response = await client.delete(
        f'/api/admin/code-tasks/{seeded_tasks_tree.code_task_id}',
        headers=author_auth_headers,
    )
    assert response.status_code == 204

    structure_response = await client.get(
        f'/api/courses/{seeded_tasks_tree.course_id}/structure'
    )
    assert structure_response.status_code == 200
    section = structure_response.json()['modules'][0]['sections'][0]
    assert seeded_tasks_tree.code_task_id not in section['code_task_ids']
    assert all(
        item['id'] != seeded_tasks_tree.code_task_id for item in section['code_tasks']
    )

    get_response = await client.get(
        f'/api/code-tasks/{seeded_tasks_tree.code_task_id}'
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_cannot_delete_task_with_student_attempts(
    client,
    author_auth_headers,
    student_auth_headers,
    seeded_tasks_tree,
):
    attempt_response = await client.post(
        f'/api/learning/tasks/{seeded_tasks_tree.task_id}/attempts',
        headers=student_auth_headers,
        json={'submitted_answer': 'GET'},
    )
    assert attempt_response.status_code == 201

    delete_response = await client.delete(
        f'/api/admin/tasks/{seeded_tasks_tree.task_id}',
        headers=author_auth_headers,
    )
    assert delete_response.status_code == 400

    get_response = await client.get(f'/api/tasks/{seeded_tasks_tree.task_id}')
    assert get_response.status_code == 200


@pytest.mark.asyncio
async def test_cannot_delete_code_task_with_submissions(
    client,
    author_auth_headers,
    student_auth_headers,
    seeded_tasks_tree,
    monkeypatch,
):
    monkeypatch.setattr(RedisSubmissionQueue, 'enqueue', AsyncMock())

    submission_response = await client.post(
        f'/api/learning/code-tasks/{seeded_tasks_tree.code_task_id}/submissions',
        headers=student_auth_headers,
        json={'source_code': 'print("hello")'},
    )
    assert submission_response.status_code == 202

    delete_response = await client.delete(
        f'/api/admin/code-tasks/{seeded_tasks_tree.code_task_id}',
        headers=author_auth_headers,
    )
    assert delete_response.status_code == 400

    get_response = await client.get(
        f'/api/code-tasks/{seeded_tasks_tree.code_task_id}'
    )
    assert get_response.status_code == 200


@pytest.mark.asyncio
async def test_delete_test_case_before_and_after_submission(
    client,
    author_auth_headers,
    student_auth_headers,
    seeded_tasks_tree,
    monkeypatch,
):
    monkeypatch.setattr(RedisSubmissionQueue, 'enqueue', AsyncMock())

    first_create_response = await client.post(
        f'/api/admin/code-tasks/{seeded_tasks_tree.code_task_id}/test-cases',
        headers=author_auth_headers,
        json={
            'position': 1,
            'input_data': '1 2',
            'expected_output': '3',
            'is_hidden': False,
            'explanation': '',
        },
    )
    assert first_create_response.status_code == 201
    first_test_case_id = first_create_response.json()['id']

    second_create_response = await client.post(
        f'/api/admin/code-tasks/{seeded_tasks_tree.code_task_id}/test-cases',
        headers=author_auth_headers,
        json={
            'position': 2,
            'input_data': '2 2',
            'expected_output': '4',
            'is_hidden': False,
            'explanation': '',
        },
    )
    assert second_create_response.status_code == 201
    second_test_case_id = second_create_response.json()['id']

    delete_response = await client.delete(
        f'/api/admin/test-cases/{first_test_case_id}',
        headers=author_auth_headers,
    )
    assert delete_response.status_code == 204

    submission_response = await client.post(
        f'/api/learning/code-tasks/{seeded_tasks_tree.code_task_id}/submissions',
        headers=student_auth_headers,
        json={'source_code': 'print(4)'},
    )
    assert submission_response.status_code == 202

    delete_blocked_response = await client.delete(
        f'/api/admin/test-cases/{second_test_case_id}',
        headers=author_auth_headers,
    )
    assert delete_blocked_response.status_code == 400


@pytest.mark.asyncio
async def test_cannot_delete_single_test_case(
    client,
    author_auth_headers,
    seeded_tasks_tree,
    session_factory,
):
    create_response = await client.post(
        f'/api/admin/code-tasks/{seeded_tasks_tree.code_task_id}/test-cases',
        headers=author_auth_headers,
        json={
            'position': 1,
            'input_data': '10 20',
            'expected_output': '30',
            'is_hidden': False,
            'explanation': '',
        },
    )
    assert create_response.status_code == 201
    test_case_id = create_response.json()['id']

    delete_response = await client.delete(
        f'/api/admin/test-cases/{test_case_id}',
        headers=author_auth_headers,
    )
    assert delete_response.status_code == 400

    async with session_factory() as session:
        model = await session.get(TestCaseModel, str(test_case_id))
        assert model is not None
