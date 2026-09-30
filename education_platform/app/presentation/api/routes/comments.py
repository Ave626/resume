from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.application.use_cases.comments import (
    CreateCommentCommand,
    CreateCommentUseCase,
    DeleteCommentCommand,
    DeleteCommentUseCase,
    GetCommentsByTargetQuery,
    GetCommentsByTargetUseCase,
    UpdateCommentCommand,
    UpdateCommentUseCase,
)
from app.domain.entities.comment import CommentTarget, CommentTargetType
from app.domain.entities.user import User
from app.presentation.api.dependencies import (
    get_create_comment_use_case,
    get_current_user,
    get_current_user_or_none,
    get_delete_comment_use_case,
    get_get_comments_by_target_use_case,
    get_update_comment_use_case,
)
from app.presentation.api.schemas import (
    CommentResponse,
    CreateCommentRequest,
    CreateLectureCommentRequest,
    ErrorResponse,
    UpdateCommentRequest,
)

router = APIRouter(tags=["Comments"])


@router.get(
    "/comments",
    response_model=list[CommentResponse],
    summary="Get comments by target",
    description="Returns comments for a specific learning target (lecture, task, code task, question).",
    responses={
        404: {"description": "Target content not found.", "model": ErrorResponse},
    },
)
async def get_comments_by_target(
    target_type: Annotated[CommentTargetType, Query(description="Target type")],
    target_id: Annotated[UUID, Query(description="Target entity ID")],
    current_user: Annotated[User | None, Depends(get_current_user_or_none)],
    use_case: Annotated[
        GetCommentsByTargetUseCase, Depends(get_get_comments_by_target_use_case)
    ],
) -> list[CommentResponse]:
    result = await use_case.execute(
        GetCommentsByTargetQuery(
            target=CommentTarget(type=target_type, id=target_id),
            actor=current_user,
        )
    )
    return [CommentResponse.model_validate(c) for c in result]


@router.post(
    "/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create comment",
    description="Creates a comment on a target content entity if actor has access.",
    responses={
        400: {"description": "Invalid comment content.", "model": ErrorResponse},
        401: {"description": "Authentication required.", "model": ErrorResponse},
        403: {
            "description": "Access denied to target content.",
            "model": ErrorResponse,
        },
        404: {"description": "Target content not found.", "model": ErrorResponse},
    },
)
async def create_comment(
    request: CreateCommentRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[CreateCommentUseCase, Depends(get_create_comment_use_case)],
) -> CommentResponse:
    result = await use_case.execute(
        CreateCommentCommand(
            target=CommentTarget(type=request.target_type, id=request.target_id),
            text=request.text,
            actor=current_user,
        )
    )
    return CommentResponse.model_validate(result)


@router.patch(
    "/comments/{comment_id}",
    response_model=CommentResponse,
    summary="Update comment",
    description="Updates comment content. Only comment author can update.",
    responses={
        400: {"description": "Invalid comment content.", "model": ErrorResponse},
        401: {"description": "Authentication required.", "model": ErrorResponse},
        403: {
            "description": "Forbidden - only author can edit.",
            "model": ErrorResponse,
        },
        404: {"description": "Comment not found.", "model": ErrorResponse},
    },
)
@router.put(
    "/comments/{comment_id}",
    response_model=CommentResponse,
    summary="Update comment",
    description="Updates comment content. Only comment author can update.",
    responses={
        400: {"description": "Invalid comment content.", "model": ErrorResponse},
        401: {"description": "Authentication required.", "model": ErrorResponse},
        403: {
            "description": "Forbidden - only author can edit.",
            "model": ErrorResponse,
        },
        404: {"description": "Comment not found.", "model": ErrorResponse},
    },
)
async def update_comment(
    comment_id: UUID,
    request: UpdateCommentRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[UpdateCommentUseCase, Depends(get_update_comment_use_case)],
) -> CommentResponse:
    result = await use_case.execute(
        UpdateCommentCommand(
            comment_id=comment_id,
            text=request.text,
            actor=current_user,
        )
    )
    return CommentResponse.model_validate(result)


@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete comment",
    description="Deletes comment. Author, course author, or admin can delete.",
    responses={
        401: {"description": "Authentication required.", "model": ErrorResponse},
        403: {
            "description": "Forbidden - insufficient permissions.",
            "model": ErrorResponse,
        },
        404: {"description": "Comment not found.", "model": ErrorResponse},
    },
)
async def delete_comment(
    comment_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[DeleteCommentUseCase, Depends(get_delete_comment_use_case)],
) -> None:
    await use_case.execute(
        DeleteCommentCommand(
            comment_id=comment_id,
            actor=current_user,
        )
    )


@router.get(
    "/lectures/{lecture_id}/comments",
    response_model=list[CommentResponse],
    summary="Get lecture comments",
    description="Returns comments for a specific lecture.",
    responses={
        404: {"description": "Lecture not found.", "model": ErrorResponse},
    },
)
async def get_lecture_comments(
    lecture_id: UUID,
    current_user: Annotated[User | None, Depends(get_current_user_or_none)],
    use_case: Annotated[
        GetCommentsByTargetUseCase, Depends(get_get_comments_by_target_use_case)
    ],
) -> list[CommentResponse]:
    result = await use_case.execute(
        GetCommentsByTargetQuery(
            target=CommentTarget(type=CommentTargetType.LECTURE, id=lecture_id),
            actor=current_user,
        )
    )
    return [CommentResponse.model_validate(c) for c in result]


@router.post(
    "/lectures/{lecture_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create lecture comment",
    description="Creates a comment on a lecture.",
    responses={
        400: {"description": "Invalid comment content.", "model": ErrorResponse},
        401: {"description": "Authentication required.", "model": ErrorResponse},
        403: {"description": "Access denied to lecture.", "model": ErrorResponse},
        404: {"description": "Lecture not found.", "model": ErrorResponse},
    },
)
async def create_lecture_comment(
    lecture_id: UUID,
    request: CreateLectureCommentRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[CreateCommentUseCase, Depends(get_create_comment_use_case)],
) -> CommentResponse:
    result = await use_case.execute(
        CreateCommentCommand(
            target=CommentTarget(type=CommentTargetType.LECTURE, id=lecture_id),
            text=request.text,
            actor=current_user,
        )
    )
    return CommentResponse.model_validate(result)
