from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.models.base import Base


class CommentModel(Base):
    __tablename__ = "comments"

    __table_args__ = (
        CheckConstraint(
            "(CASE WHEN lecture_id IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN question_id IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN task_id IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN code_task_id IS NOT NULL THEN 1 ELSE 0 END) = 1",
            name="ck_comments_single_target",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    text: Mapped[str] = mapped_column(String(2000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    lecture_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("lectures.id", ondelete="CASCADE"),
        nullable=True,
    )
    question_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=True,
    )
    task_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=True,
    )
    code_task_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("code_tasks.id", ondelete="CASCADE"),
        nullable=True,
    )
