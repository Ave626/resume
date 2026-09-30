from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.domain.entities.comment import Comment, CommentTarget, CommentTargetType
from app.domain.exceptions import InvalidCommentError


def test_comment_strips_text_whitespace():
    target = CommentTarget(type=CommentTargetType.LECTURE, id=uuid4())
    comment = Comment(
        id=uuid4(),
        target=target,
        user_id=uuid4(),
        text="   Important note on clean architecture   ",
        created_at=datetime.now(UTC),
    )

    assert comment.text == "Important note on clean architecture"


def test_empty_comment_text_is_rejected():
    target = CommentTarget(type=CommentTargetType.LECTURE, id=uuid4())
    with pytest.raises(InvalidCommentError):
        Comment(
            id=uuid4(),
            target=target,
            user_id=uuid4(),
            text="   ",
            created_at=datetime.now(UTC),
        )


def test_comment_text_exceeding_max_length_is_rejected():
    target = CommentTarget(type=CommentTargetType.LECTURE, id=uuid4())
    with pytest.raises(InvalidCommentError):
        Comment(
            id=uuid4(),
            target=target,
            user_id=uuid4(),
            text="a" * 2001,
            created_at=datetime.now(UTC),
        )


def test_update_comment_changes_text_and_updated_at():
    target = CommentTarget(type=CommentTargetType.LECTURE, id=uuid4())
    initial_time = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    comment = Comment(
        id=uuid4(),
        target=target,
        user_id=uuid4(),
        text="Original text",
        created_at=initial_time,
    )

    assert comment.updated_at is None

    comment.update_text("   Updated text with whitespace   ")

    assert comment.text == "Updated text with whitespace"
    assert comment.updated_at is not None
    assert comment.updated_at > initial_time


def test_update_comment_with_empty_text_is_rejected():
    target = CommentTarget(type=CommentTargetType.LECTURE, id=uuid4())
    comment = Comment(
        id=uuid4(),
        target=target,
        user_id=uuid4(),
        text="Original text",
        created_at=datetime.now(UTC),
    )

    with pytest.raises(InvalidCommentError):
        comment.update_text("   ")
