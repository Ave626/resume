import pytest
from sqlalchemy import select

from app.infrastructure.database.models import (
    ProgressModel,
    QuestionAttemptModel,
    QuestionModel,
)


@pytest.mark.asyncio
async def test_interactive_flow_from_author_setup_to_student_progress(
    client,
    author_auth_headers,
    student_auth_headers,
    session_factory,
):
    course_response = await client.post(
        "/api/admin/courses",
        headers=author_auth_headers,
        json={
            "title": "Interactive FastAPI",
            "description": "Course with questions inside sections.",
        },
    )
    course_id = course_response.json()["id"]

    module_response = await client.post(
        f"/api/admin/courses/{course_id}/modules",
        headers=author_auth_headers,
        json={"title": "HTTP", "description": "Methods", "position": 1},
    )
    module_id = module_response.json()["id"]

    section_response = await client.post(
        f"/api/admin/modules/{module_id}/sections",
        headers=author_auth_headers,
        json={"title": "Basics", "description": "Intro", "position": 1},
    )
    section_id = section_response.json()["id"]

    question_response = await client.post(
        f"/api/admin/sections/{section_id}/questions",
        headers=author_auth_headers,
        json={
            "text": "Which method reads a resource?",
            "position": 1,
            "question_type": "single_choice",
            "max_attempts": 2,
            "reward_points": 5,
        },
    )
    question_id = question_response.json()["id"]

    await client.post(
        f"/api/admin/questions/{question_id}/answer-options",
        headers=author_auth_headers,
        json={"text": "POST", "position": 1, "is_correct": False},
    )
    correct_option_response = await client.post(
        f"/api/admin/questions/{question_id}/answer-options",
        headers=author_auth_headers,
        json={"text": "GET", "position": 2, "is_correct": True},
    )
    correct_option_id = correct_option_response.json()["id"]

    start_response = await client.get(
        f"/api/learning/questions/{question_id}/attempt",
        headers=student_auth_headers,
    )
    assert start_response.status_code == 200

    submit_response = await client.post(
        f"/api/learning/questions/{question_id}/attempts",
        headers=student_auth_headers,
        json={"selected_option_ids": [correct_option_id]},
    )
    assert submit_response.status_code == 201

    async with session_factory() as session:
        attempts = (await session.execute(select(QuestionAttemptModel))).scalars().all()
        progress_items = (await session.execute(select(ProgressModel))).scalars().all()

    assert len(attempts) == 1
    assert len(progress_items) == 1
    assert progress_items[0].total_points == 5


@pytest.mark.asyncio
async def test_author_can_delete_answer_option_and_question(
    client,
    author_auth_headers,
    student_auth_headers,
    session_factory,
):
    course_res = await client.post(
        "/api/admin/courses",
        headers=author_auth_headers,
        json={"title": "Architecture Course", "description": "DDD and Clean Arch"},
    )
    course_id = course_res.json()["id"]

    module_res = await client.post(
        f"/api/admin/courses/{course_id}/modules",
        headers=author_auth_headers,
        json={"title": "Interactive Module", "description": "Tests", "position": 1},
    )
    module_id = module_res.json()["id"]

    section_res = await client.post(
        f"/api/admin/modules/{module_id}/sections",
        headers=author_auth_headers,
        json={
            "title": "Quiz Section",
            "description": "Section with questions",
            "position": 1,
        },
    )
    section_id = section_res.json()["id"]

    question_res = await client.post(
        f"/api/admin/sections/{section_id}/questions",
        headers=author_auth_headers,
        json={
            "text": "What does HTTP 204 mean?",
            "position": 1,
            "question_type": "single_choice",
            "max_attempts": 3,
            "reward_points": 10,
        },
    )
    assert question_res.status_code == 201
    question_id = question_res.json()["id"]

    opt1_res = await client.post(
        f"/api/admin/questions/{question_id}/answer-options",
        headers=author_auth_headers,
        json={"text": "Bad Request", "position": 1, "is_correct": False},
    )
    opt1_id = opt1_res.json()["id"]

    await client.post(
        f"/api/admin/questions/{question_id}/answer-options",
        headers=author_auth_headers,
        json={"text": "Not Found", "position": 2, "is_correct": False},
    )

    await client.post(
        f"/api/admin/questions/{question_id}/answer-options",
        headers=author_auth_headers,
        json={"text": "No Content", "position": 3, "is_correct": True},
    )

    del_opt_res = await client.delete(
        f"/api/admin/answer-options/{opt1_id}",
        headers=author_auth_headers,
    )
    assert del_opt_res.status_code == 204

    attempt_context = await client.get(
        f"/api/learning/questions/{question_id}/attempt",
        headers=student_auth_headers,
    )
    assert attempt_context.status_code == 200
    options = attempt_context.json()["answer_options"]
    assert len(options) == 2
    assert opt1_id not in [o["id"] for o in options]

    del_q_res = await client.delete(
        f"/api/admin/questions/{question_id}",
        headers=author_auth_headers,
    )
    assert del_q_res.status_code == 204

    missing_q_res = await client.get(
        f"/api/learning/questions/{question_id}/attempt",
        headers=student_auth_headers,
    )
    assert missing_q_res.status_code == 404
    assert missing_q_res.json()["error"] == "question_not_found"

    async with session_factory() as session:
        questions_in_db = (
            (
                await session.execute(
                    select(QuestionModel).where(QuestionModel.section_id == section_id)
                )
            )
            .scalars()
            .all()
        )
        assert len(questions_in_db) == 0


@pytest.mark.asyncio
async def test_cannot_delete_question_or_option_after_student_attempt(
    client,
    author_auth_headers,
    student_auth_headers,
    session_factory,
):
    course_res = await client.post(
        "/api/admin/courses",
        headers=author_auth_headers,
        json={"title": "Interactive FastAPI", "description": "Course with attempts."},
    )
    course_id = course_res.json()["id"]

    module_res = await client.post(
        f"/api/admin/courses/{course_id}/modules",
        headers=author_auth_headers,
        json={"title": "Module 1", "description": "Desc", "position": 1},
    )
    module_id = module_res.json()["id"]

    section_res = await client.post(
        f"/api/admin/modules/{module_id}/sections",
        headers=author_auth_headers,
        json={"title": "Section 1", "description": "Desc", "position": 1},
    )
    section_id = section_res.json()["id"]

    question_res = await client.post(
        f"/api/admin/sections/{section_id}/questions",
        headers=author_auth_headers,
        json={
            "text": "What does POST usually do?",
            "position": 1,
            "question_type": "single_choice",
            "max_attempts": 2,
            "reward_points": 5,
        },
    )
    question_id = question_res.json()["id"]

    wrong_opt_res = await client.post(
        f"/api/admin/questions/{question_id}/answer-options",
        headers=author_auth_headers,
        json={"text": "Reads resource", "position": 1, "is_correct": False},
    )
    wrong_opt_id = wrong_opt_res.json()["id"]

    correct_opt_res = await client.post(
        f"/api/admin/questions/{question_id}/answer-options",
        headers=author_auth_headers,
        json={"text": "Creates resource", "position": 2, "is_correct": True},
    )
    correct_opt_id = correct_opt_res.json()["id"]

    submit_res = await client.post(
        f"/api/learning/questions/{question_id}/attempts",
        headers=student_auth_headers,
        json={"selected_option_ids": [correct_opt_id]},
    )
    assert submit_res.status_code == 201

    del_opt_res = await client.delete(
        f"/api/admin/answer-options/{wrong_opt_id}",
        headers=author_auth_headers,
    )
    assert del_opt_res.status_code == 400

    del_q_res = await client.delete(
        f"/api/admin/questions/{question_id}",
        headers=author_auth_headers,
    )
    assert del_q_res.status_code == 400

    async with session_factory() as session:
        attempts = (await session.execute(select(QuestionAttemptModel))).scalars().all()
        progress_items = (await session.execute(select(ProgressModel))).scalars().all()
        questions = (await session.execute(select(QuestionModel))).scalars().all()

    assert len(attempts) == 1
    assert len(progress_items) == 1
    assert len(questions) == 1
    assert progress_items[0].total_points == 5
