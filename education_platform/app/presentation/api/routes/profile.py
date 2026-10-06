from uuid import UUID

from fastapi import APIRouter, Depends

from app.application.use_cases.activity.get_my_activity import (
    GetMyActivitiesCommand,
    GetMyActivitiesUseCase,
)
from app.application.use_cases.profile.get_my_course_analytics import (
    GetMyCourseAnalyticsQuery,
    GetMyCourseAnalyticsUseCase,
)
from app.application.use_cases.profile.get_my_profile import (
    GetMyProfileQuery,
    GetMyProfileUseCase,
)
from app.application.use_cases.profile.get_my_teaching_course_analytics import (
    GetMyTeachingCourseAnalyticsQuery,
    GetMyTeachingCourseAnalyticsUseCase,
)
from app.application.use_cases.profile.update_my_profile import (
    UpdateMyProfileCommand,
    UpdateMyProfileUseCase,
)
from app.domain.entities.user import User
from app.presentation.api.dependencies import (
    get_current_user,
    get_get_my_activities_use_case,
    get_get_my_course_analytics,
    get_get_my_profile_use_case,
    get_get_my_teaching_course_analytics_use_case,
    get_update_my_profile_use_case,
)
from app.presentation.api.schemas import (
    AuthorCourseAnalyticsResponse,
    ErrorResponse,
    StudentActivityResponse,
    StudentCourseAnalyticsResponse,
    UpdateMyProfileRequest,
    UserProfileResponse,
)

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Get my profile",
    description="Returns the current authenticated user profile.",
    responses={
        401: {
            "description": "Authentication credentials are missing or invalid.",
            "model": ErrorResponse,
        },
    },
)
async def get_my_profile(
    actor: User = Depends(get_current_user),
    use_case: GetMyProfileUseCase = Depends(get_get_my_profile_use_case),
) -> UserProfileResponse:
    result = await use_case.execute(GetMyProfileQuery(actor=actor))
    return UserProfileResponse.model_validate(result)


@router.patch(
    "/me",
    response_model=UserProfileResponse,
    summary="Update my profile",
    description="Updates the current authenticated user profile.",
    responses={
        401: {
            "description": "Authentication credentials are missing or invalid.",
            "model": ErrorResponse,
        },
    },
)
async def update_my_profile(
    request: UpdateMyProfileRequest,
    actor: User = Depends(get_current_user),
    use_case: UpdateMyProfileUseCase = Depends(get_update_my_profile_use_case),
) -> UserProfileResponse:
    result = await use_case.execute(
        UpdateMyProfileCommand(
            actor=actor,
            full_name=request.full_name,
            bio=request.bio,
            avatar_url=str(request.avatar_url)
            if request.avatar_url is not None
            else None,
        )
    )
    return UserProfileResponse.model_validate(result)


@router.get(
    "/me/courses/{course_id}/analytics",
    response_model=StudentCourseAnalyticsResponse,
    summary="Get my course analytics",
    description="Returns learning analytics of the current student for the selected course.",
    responses={
        401: {
            "description": "Authentication credentials are missing or invalid.",
            "model": ErrorResponse,
        },
        403: {
            "description": "User cannot view own learning analytics.",
            "model": ErrorResponse,
        },
        404: {
            "description": "Course was not found.",
            "model": ErrorResponse,
        },
    },
)
async def get_my_course_analytics(
    course_id: UUID,
    user: User = Depends(get_current_user),
    use_case: GetMyCourseAnalyticsUseCase = Depends(get_get_my_course_analytics),
) -> StudentCourseAnalyticsResponse:
    result = await use_case.execute(
        GetMyCourseAnalyticsQuery(actor=user, course_id=course_id)
    )
    return StudentCourseAnalyticsResponse.model_validate(result)


@router.get(
    "/me/teaching/courses/{course_id}/analytics",
    response_model=AuthorCourseAnalyticsResponse,
    summary="Get teaching analytics for my course",
    description="Returns aggregated teaching analytics for a course owned by the current author.",
    responses={
        401: {
            "description": "Authentication credentials are missing or invalid.",
            "model": ErrorResponse,
        },
        403: {
            "description": "User cannot view teaching analytics for this course.",
            "model": ErrorResponse,
        },
        404: {
            "description": "Course was not found.",
            "model": ErrorResponse,
        },
    },
)
async def get_my_teaching_course_analytics(
    course_id: UUID,
    actor: User = Depends(get_current_user),
    use_case: GetMyTeachingCourseAnalyticsUseCase = Depends(
        get_get_my_teaching_course_analytics_use_case,
    ),
) -> AuthorCourseAnalyticsResponse:
    result = await use_case.execute(
        GetMyTeachingCourseAnalyticsQuery(actor=actor, course_id=course_id)
    )
    return AuthorCourseAnalyticsResponse.model_validate(result)

@router.get(
    "/me/activities",
    response_model=list[StudentActivityResponse],
    summary="Get my activities",
    description="Returns activities of the current authenticated user.",
    responses={
        401: {
            "description": "Authentication credentials are missing or invalid.",
            "model": ErrorResponse,
        },
    },
)
async def get_my_activities(
    limit : int = 20,
    offset : int = 0,
    actor : User = Depends(get_current_user),
    use_case : GetMyActivitiesUseCase = Depends(get_get_my_activities_use_case)
) -> list[StudentActivityResponse]:
    result = await use_case.execute(
        GetMyActivitiesCommand(actor=actor, limit=limit, offset=offset)
    )
    return [StudentActivityResponse.model_validate(item) for item in result]
    