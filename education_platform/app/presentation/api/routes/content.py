from uuid import UUID

from fastapi import APIRouter, Depends, Security,Query

from app.application.use_cases.courses.get_course import (
    GetCourseQuery,
    GetCourseUseCase,
)
from app.application.use_cases.courses.get_course_structure import (
    GetCourseStructureQuery,
    GetCourseStructureUseCase,
)
from app.application.use_cases.courses.get_courses import (
    GetCoursesQuery,
    GetCoursesUseCase,
)
from app.application.use_cases.lectures.get_lecture import (
    GetLectureQuery,
    GetLectureUseCase,
)
from app.domain.entities.course import CourseDifficulty
from app.presentation.api.dependencies import (
    get_get_course_structure_use_case,
    get_get_course_use_case,
    get_get_courses_use_case,
    get_get_lecture_use_case,
    get_current_user_or_none,
)
from app.presentation.api.schemas import (
    CourseListItemResponse,
    CourseResponse,
    CourseStructureResponse,
    ErrorResponse,
    LectureResponse,
)
from app.presentation.api.schemas import (
    CourseCatalogCardResponse,
    CourseCatalogItemResponse,
    CourseStructureResponse,
    ErrorResponse,
    LectureResponse,
)
from app.application.use_cases.questions.get_question import (
    GetQuestionQuery,
    GetQuestionUseCase,
)
from app.application.use_cases.tasks.get_task import GetTaskQuery, GetTaskUseCase
from app.application.use_cases.code_tasks.get_code_task import (
    GetCodeTaskQuery,
    GetCodeTaskUseCase,
)
from app.presentation.api.dependencies import (
    get_get_code_task_use_case,
    get_get_question_use_case,
    get_get_task_use_case,
)
from app.presentation.api.schemas import (
    CodeTaskDetailsResponse,
    QuestionDetailsResponse,
    TaskDetailsResponse,
)
from app.domain.entities.user import User

router = APIRouter(tags=["Content"])


@router.get(
    '/courses',
    response_model=list[CourseCatalogItemResponse],
    summary='Get public course catalog',
    description='Returns published courses formatted for catalog listing.',
)
async def get_courses(
        search: str = Query(default=''),
        difficulty: CourseDifficulty | None = Query(default=None),
        tag: list[str] = Query(default=[]),
        use_case: GetCoursesUseCase = Depends(get_get_courses_use_case),
) -> list[CourseCatalogItemResponse]:
    result = await use_case.execute(
        GetCoursesQuery(
            search=search,
            difficulty=difficulty,
            tag_names=list(tag),
        )
    )
    return [CourseCatalogItemResponse.model_validate(course) for course in result]

@router.get(
    '/courses/{course_id}',
    response_model=CourseCatalogCardResponse,
    summary='Get public course page',
    description='Returns a detailed course card for the catalog page.',
    responses={
        404: {
            'description': 'Course was not found.',
            'model': ErrorResponse,
        },
    },
)
async def get_course(
        course_id: UUID,
        current_user: User | None = Depends(get_current_user_or_none),
        use_case: GetCourseUseCase = Depends(get_get_course_use_case),
) -> CourseCatalogCardResponse:
    result = await use_case.execute(
        GetCourseQuery(
            course_id=course_id,
            actor=current_user,
        )
    )
    return CourseCatalogCardResponse.model_validate(result)


@router.get(
    "/courses/{course_id}/structure",
    response_model=CourseStructureResponse,
    summary="Get course structure",
    description=(
            "Returns the course navigation tree: modules, sections and lectures "
            "without full lecture content."
    ),
    responses={
        404: {
            "description": "Course was not found.",
            "model": ErrorResponse,
        },
    },
)
async def get_course_structure(
        course_id: UUID,
        current_user: User | None = Depends(get_current_user_or_none),
        use_case: GetCourseStructureUseCase = Depends(get_get_course_structure_use_case),
) -> CourseStructureResponse:
    result = await use_case.execute(
        GetCourseStructureQuery(
            course_id=course_id,
            actor=current_user,
        )
    )
    return CourseStructureResponse.model_validate(result)


@router.get(
    "/lectures/{lecture_id}",
    response_model=LectureResponse,
    summary="Get lecture by ID",
    description="Returns the full content of a single lecture.",
    responses={
        404: {
            "description": "Lecture was not found.",
            "model": ErrorResponse,
        },
    },
)
async def get_lecture(
        lecture_id: UUID,
        current_user: User | None = Depends(get_current_user_or_none),
        use_case: GetLectureUseCase = Depends(get_get_lecture_use_case),
) -> LectureResponse:
    result = await use_case.execute(
        GetLectureQuery(
            lecture_id=lecture_id,
            actor=current_user,
        )
    )
    return LectureResponse.model_validate(result)

@router.get(
    '/questions/{question_id}',
    response_model=QuestionDetailsResponse,
    summary='Get question by ID',
    description='Returns the content of a single question with public answer options.',
)
async def get_question(
    question_id: UUID,
    current_user: User | None = Depends(get_current_user_or_none),
    use_case: GetQuestionUseCase = Depends(get_get_question_use_case),
) -> QuestionDetailsResponse:
    result = await use_case.execute(
        GetQuestionQuery(
            question_id=question_id,
            actor=current_user,
        )
    )
    return QuestionDetailsResponse.model_validate(result)

@router.get(
    '/tasks/{task_id}',
    response_model=TaskDetailsResponse,
    summary='Get task by ID',
    description='Returns the content of a single task without author check configuration.',
)
async def get_task(
    task_id: UUID,
    use_case: GetTaskUseCase = Depends(get_get_task_use_case),
    current_user : User | None = Depends(get_current_user_or_none)
) -> TaskDetailsResponse:
    result = await use_case.execute(
        GetTaskQuery(
            task_id=task_id,
            actor=current_user
            )
        )
    return TaskDetailsResponse.model_validate(result)


@router.get(
    '/code-tasks/{code_task_id}',
    response_model=CodeTaskDetailsResponse,
    summary='Get code task by ID',
    description='Returns the content of a single code task and its editor configuration.',
)
async def get_code_task(
    code_task_id: UUID,
    current_user: User | None = Depends(get_current_user_or_none),
    use_case: GetCodeTaskUseCase = Depends(get_get_code_task_use_case),
) -> CodeTaskDetailsResponse:
    result = await use_case.execute(
        GetCodeTaskQuery(
            code_task_id=code_task_id,
            actor=current_user,
        )
    )
    return CodeTaskDetailsResponse.model_validate(result)