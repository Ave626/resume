from uuid import UUID

from app.domain.entities.comment import Comment, CommentTarget, CommentTargetType
from app.infrastructure.database.models.comment_model import CommentModel


class CommentMapper:
    @staticmethod
    def to_domain(model: CommentModel) -> Comment:
        if model.lecture_id is not None:
            target = CommentTarget(
                type=CommentTargetType.LECTURE, id=UUID(model.lecture_id)
            )
        elif model.question_id is not None:
            target = CommentTarget(
                type=CommentTargetType.QUESTION, id=UUID(model.question_id)
            )
        elif model.task_id is not None:
            target = CommentTarget(type=CommentTargetType.TASK, id=UUID(model.task_id))
        elif model.code_task_id is not None:
            target = CommentTarget(
                type=CommentTargetType.CODE_TASK, id=UUID(model.code_task_id)
            )
        else:
            raise ValueError(f"Comment {model.id} has no valid target foreign key.")

        return Comment(
            id=UUID(model.id),
            target=target,
            user_id=UUID(model.user_id),
            text=model.text,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(comment: Comment) -> CommentModel:
        return CommentModel(
            id=str(comment.id),
            user_id=str(comment.user_id),
            text=comment.text,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            lecture_id=(
                str(comment.target.id)
                if comment.target.type == CommentTargetType.LECTURE
                else None
            ),
            question_id=(
                str(comment.target.id)
                if comment.target.type == CommentTargetType.QUESTION
                else None
            ),
            task_id=(
                str(comment.target.id)
                if comment.target.type == CommentTargetType.TASK
                else None
            ),
            code_task_id=(
                str(comment.target.id)
                if comment.target.type == CommentTargetType.CODE_TASK
                else None
            ),
        )
