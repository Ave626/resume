import pytest
from sqlalchemy import inspect


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("table_name", "expected_indexes"),
    [
        (
            "courses",
            {"ix_courses_status_difficulty"},
        ),
        (
            "modules",
            {"ix_modules_course_position"},
        ),
        (
            "sections",
            {"ix_sections_module_position"},
        ),
        (
            "lectures",
            {"ix_lectures_section_position"},
        ),
        (
            "questions",
            {"ix_questions_section_position"},
        ),
        (
            "tasks",
            {"ix_tasks_section_position"},
        ),
        (
            "code_tasks",
            {"ix_code_tasks_section_position"},
        ),
        (
            "answer_options",
            {"ix_answer_options_question_position"},
        ),
        (
            "test_cases",
            {"ix_test_cases_code_task_position"},
        ),
        (
            "progress",
            {"ix_progress_course_id"},
        ),
        (
            "question_attempts",
            {
                "ix_question_attempts_student_question_number",
                "ix_question_attempts_question_student_number",
            },
        ),
        (
            "task_attempts",
            {
                "ix_task_attempts_student_task_number",
                "ix_task_attempts_task_number",
            },
        ),
        (
            "code_submissions",
            {"ix_code_submissions_task_number"},
        ),
    ],
)
async def test_read_indexes_exist(
    test_engine,
    table_name,
    expected_indexes,
):
    async with test_engine.connect() as connection:
        indexes = await connection.run_sync(
            lambda sync_connection: inspect(sync_connection).get_indexes(table_name)
        )
        actual_names = {index["name"] for index in indexes}
        assert expected_indexes <= actual_names
