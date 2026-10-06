from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.domain.entities.student_activity import StudentActivity, StudentActivityType
from app.domain.exceptions import InvalidStudentActivityError


def test_student_activity_creation_success():
    activity_id = uuid4()
    student_id = uuid4()
    course_id = uuid4()
    entity_id = uuid4()
    activity = StudentActivity(
        id=activity_id,
        student_id=student_id,
        course_id=course_id,
        activity_type=StudentActivityType.QUESTION_COMPLETED,
        entity_id=entity_id,
        title="Completed quiz question",
        details={"points": 5, "option_selected": "A"},
    )

    assert activity.id == activity_id
    assert activity.student_id == student_id
    assert activity.course_id == course_id
    assert activity.activity_type == StudentActivityType.QUESTION_COMPLETED
    assert activity.entity_id == entity_id
    assert activity.title == "Completed quiz question"
    assert activity.details == {"points": 5, "option_selected": "A"}
    assert activity.occurred_at.tzinfo is not None


def test_student_activity_strips_title_whitespace():
    activity = StudentActivity(
        id=uuid4(),
        student_id=uuid4(),
        course_id=uuid4(),
        activity_type=StudentActivityType.TASK_COMPLETED,
        entity_id=uuid4(),
        title="   Submitted task solution   ",
    )

    assert activity.title == "Submitted task solution"
    assert activity.details == {}


def test_student_activity_empty_title_raises_error():
    with pytest.raises(InvalidStudentActivityError):
        StudentActivity(
            id=uuid4(),
            student_id=uuid4(),
            course_id=uuid4(),
            activity_type=StudentActivityType.CODE_TASK_COMPLETED,
            entity_id=uuid4(),
            title="   ",
        )


def test_student_activity_naive_datetime_raises_error():
    naive_dt = datetime.now(UTC).replace(tzinfo=None)
    with pytest.raises(InvalidStudentActivityError):
        StudentActivity(
            id=uuid4(),
            student_id=uuid4(),
            course_id=uuid4(),
            activity_type=StudentActivityType.MODULE_COMPLETED,
            entity_id=uuid4(),
            title="Completed module",
            occurred_at=naive_dt,
        )


def test_student_activity_none_details_defaults_to_empty_dict():
    activity = StudentActivity(
        id=uuid4(),
        student_id=uuid4(),
        course_id=uuid4(),
        activity_type=StudentActivityType.SECTION_COMPLETED,
        entity_id=uuid4(),
        title="Section finished",
        details=None,
    )

    assert activity.details == {}
