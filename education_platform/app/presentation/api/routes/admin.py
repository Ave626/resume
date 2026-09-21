from uuid import UUID

from fastapi import APIRouter, Depends, Response, status,UploadFile,File

from app.application.use_cases.courses.create_course import (
    CreateCourseCommand,
    CreateCourseUseCase,
)
from app.application.use_cases.courses.delete_course import (
    DeleteCourseCommand,
    DeleteCourseUseCase,
)
from app.application.use_cases.courses.update_course import (
    UpdateCourseCommand,
    UpdateCourseUseCase,
)
from app.application.use_cases.lectures.create_lecture import (
    CreateLectureCommand,
    CreateLectureUseCase,
)
from app.application.use_cases.lectures.delete_lecture import (
    DeleteLectureCommand,
    DeleteLectureUseCase,
)
from app.application.use_cases.lectures.update_lecture import (
    UpdateLectureCommand,
    UpdateLectureUseCase,
)
from app.application.use_cases.modules.create_module import (
    CreateModuleCommand,
    CreateModuleUseCase,
)
from app.application.use_cases.modules.delete_module import (
    DeleteModuleCommand,
    DeleteModuleUseCase,
)
from app.application.use_cases.modules.update_module import (
    UpdateModuleCommand,
    UpdateModuleUseCase,
)
from app.application.use_cases.sections.create_section import (
    CreateSectionCommand,
    CreateSectionUseCase,
)
from app.application.use_cases.sections.delete_section import (
    DeleteSectionCommand,
    DeleteSectionUseCase,
)
from app.application.use_cases.sections.update_section import (
    UpdateSectionCommand,
    UpdateSectionUseCase,
)
from app.domain.entities.user import User
from app.presentation.api.dependencies import (
    get_create_course_use_case,
    get_create_lecture_use_case,
    get_create_module_use_case,
    get_create_section_use_case,
    get_current_author_or_admin,
    get_delete_course_use_case,
    get_delete_lecture_use_case,
    get_delete_module_use_case,
    get_delete_section_use_case,
    get_update_course_use_case,
    get_update_lecture_use_case,
    get_update_module_use_case,
    get_update_section_use_case,
    get_archive_course_use_case,  
    get_publish_course_use_case, 
    get_get_course_publication_readiness_use_case,
    get_upload_course_cover_use_case,
)
from app.presentation.api.schemas import (
    CourseResponse,
    CreateCourseRequest,
    CreateLectureRequest,
    CreateModuleRequest,
    CreateSectionRequest,
    ErrorResponse,
    LectureResponse,
    ModuleResponse,
    SectionResponse,
    UpdateCourseRequest,
    UpdateLectureRequest,
    UpdateModuleRequest,
    UpdateSectionRequest,
    CoursePublicationErrorResponse,   
    CoursePublicationReadinessResponse,   
)
from app.application.use_cases.courses.archive_course import (
    ArchiveCourseCommand,
    ArchiveCourseUseCase,
)
from app.application.use_cases.courses.publish_course import (
    PublishCourseCommand,
    PublishCourseUseCase,
)
from app.application.use_cases.courses.get_course_publication_readiness import (
    GetCoursePublicationReadinessQuery,
    GetCoursePublicationReadinessUseCase,
)
from app.application.use_cases.courses.upload_course_cover import (
    UploadCourseCoverCommand,
    UploadCourseCoverUseCase,
)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    responses={
        401: {
            "description": "Authentication credentials are missing or invalid.",
            "model": ErrorResponse,
        },
        403: {
            "description": "Author or admin access is required.",
            "model": ErrorResponse,
        },
    },
)


@router.post(
    "/courses",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create course",
    description="Creates a new course owned by the current author or administrator.",
    responses={
        400: {
            "description": "Domain or application validation error.",
            "model": ErrorResponse,
        },
    },
)
async def create_course(
        request: CreateCourseRequest,
        actor: User = Depends(get_current_author_or_admin),
        use_case: CreateCourseUseCase = Depends(get_create_course_use_case),
) -> CourseResponse:
    result = await use_case.execute(
        CreateCourseCommand(
            actor=actor,
            title=request.title,
            description=request.description,
            short_description=request.short_description,
            cover_image_url=str(request.cover_image_url) if request.cover_image_url is not None else None,
            difficulty=request.difficulty,
            tag_names=list(request.tag_names),
        )
    )
    return CourseResponse.model_validate(result)


@router.put(
    "/courses/{course_id}",
    response_model=CourseResponse,
    summary="Update course",
    description="Updates a course if the current user owns it or manages the platform.",
    responses={
        400: {
            "description": "Domain or application validation error.",
            "model": ErrorResponse,
        },
        404: {
            "description": "Course was not found.",
            "model": ErrorResponse,
        },
    },
)
async def update_course(
        course_id: UUID,
        request: UpdateCourseRequest,
        actor: User = Depends(get_current_author_or_admin),
        use_case: UpdateCourseUseCase = Depends(get_update_course_use_case),
) -> CourseResponse:
    result = await use_case.execute(
        UpdateCourseCommand(
            actor=actor,
            course_id=course_id,
            title=request.title,
            description=request.description,
            short_description=request.short_description,
            cover_image_url=str(request.cover_image_url) if request.cover_image_url is not None else None,
            difficulty=request.difficulty,
            tag_names=list(request.tag_names),
        )
    )
    return CourseResponse.model_validate(result)


@router.delete(
    "/courses/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete course",
    description="Deletes a course together with its entire content subtree.",
    responses={
        404: {
            "description": "Course was not found.",
            "model": ErrorResponse,
        },
    },
)
async def delete_course(
    course_id: UUID,
    actor: User = Depends(get_current_author_or_admin),
    use_case: DeleteCourseUseCase = Depends(get_delete_course_use_case),
) -> Response:
    await use_case.execute(
        DeleteCourseCommand(
            actor=actor,
            course_id=course_id,
        )
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/courses/{course_id}/modules",
    response_model=ModuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create module",
    description="Creates a new module inside a course available to the current user.",
    responses={
        400: {
            "description": "Domain or application validation error.",
            "model": ErrorResponse,
        },
        404: {
            "description": "Course was not found.",
            "model": ErrorResponse,
        },
    },
)
async def create_module(
    course_id: UUID,
    request: CreateModuleRequest,
    actor: User = Depends(get_current_author_or_admin),
    use_case: CreateModuleUseCase = Depends(get_create_module_use_case),
) -> ModuleResponse:
    result = await use_case.execute(
        CreateModuleCommand(
            actor=actor,
            course_id=course_id,
            title=request.title,
            description=request.description,
            position=request.position,
        )
    )
    return ModuleResponse.model_validate(result)


@router.put(
    "/modules/{module_id}",
    response_model=ModuleResponse,
    summary="Update module",
    description="Updates a module if it belongs to a course managed by the current user.",
    responses={
        400: {
            "description": "Domain or application validation error.",
            "model": ErrorResponse,
        },
        404: {
            "description": "Module was not found.",
            "model": ErrorResponse,
        },
    },
)
async def update_module(
    module_id: UUID,
    request: UpdateModuleRequest,
    actor: User = Depends(get_current_author_or_admin),
    use_case: UpdateModuleUseCase = Depends(get_update_module_use_case),
) -> ModuleResponse:
    result = await use_case.execute(
        UpdateModuleCommand(
            actor=actor,
            module_id=module_id,
            title=request.title,
            description=request.description,
            position=request.position,
        )
    )
    return ModuleResponse.model_validate(result)


@router.delete(
    "/modules/{module_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete module",
    description="Deletes a module together with its nested sections and lectures.",
    responses={
        404: {
            "description": "Module was not found.",
            "model": ErrorResponse,
        },
    },
)
async def delete_module(
    module_id: UUID,
    actor: User = Depends(get_current_author_or_admin),
    use_case: DeleteModuleUseCase = Depends(get_delete_module_use_case),
) -> Response:
    await use_case.execute(
        DeleteModuleCommand(
            actor=actor,
            module_id=module_id,
        )
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/modules/{module_id}/sections",
    response_model=SectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create section",
    description="Creates a new section inside a module managed by the current user.",
    responses={
        400: {
            "description": "Domain or application validation error.",
            "model": ErrorResponse,
        },
        404: {
            "description": "Module was not found.",
            "model": ErrorResponse,
        },
    },
)
async def create_section(
    module_id: UUID,
    request: CreateSectionRequest,
    actor: User = Depends(get_current_author_or_admin),
    use_case: CreateSectionUseCase = Depends(get_create_section_use_case),
) -> SectionResponse:
    result = await use_case.execute(
        CreateSectionCommand(
            actor=actor,
            module_id=module_id,
            title=request.title,
            description=request.description,
            position=request.position,
        )
    )
    return SectionResponse.model_validate(result)


@router.put(
    "/sections/{section_id}",
    response_model=SectionResponse,
    summary="Update section",
    description="Updates a section if it belongs to a course managed by the current user.",
    responses={
        400: {
            "description": "Domain or application validation error.",
            "model": ErrorResponse,
        },
        404: {
            "description": "Section was not found.",
            "model": ErrorResponse,
        },
    },
)
async def update_section(
    section_id: UUID,
    request: UpdateSectionRequest,
    actor: User = Depends(get_current_author_or_admin),
    use_case: UpdateSectionUseCase = Depends(get_update_section_use_case),
) -> SectionResponse:
    result = await use_case.execute(
        UpdateSectionCommand(
            actor=actor,
            section_id=section_id,
            title=request.title,
            description=request.description,
            position=request.position,
        )
    )
    return SectionResponse.model_validate(result)


@router.delete(
    "/sections/{section_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete section",
    description="Deletes a section together with all nested lectures and activities.",
    responses={
        404: {
            "description": "Section was not found.",
            "model": ErrorResponse,
        },
    },
)
async def delete_section(
    section_id: UUID,
    actor: User = Depends(get_current_author_or_admin),
    use_case: DeleteSectionUseCase = Depends(get_delete_section_use_case),
) -> Response:
    await use_case.execute(
        DeleteSectionCommand(
            actor=actor,
            section_id=section_id,
        )
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/sections/{section_id}/lectures",
    response_model=LectureResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create lecture",
    description="Creates a lecture inside a section available to the current user.",
    responses={
        400: {
            "description": "Domain or application validation error.",
            "model": ErrorResponse,
        },
        404: {
            "description": "Section was not found.",
            "model": ErrorResponse,
        },
    },
)
async def create_lecture(
    section_id: UUID,
    request: CreateLectureRequest,
    actor: User = Depends(get_current_author_or_admin),
    use_case: CreateLectureUseCase = Depends(get_create_lecture_use_case),
) -> LectureResponse:
    result = await use_case.execute(
        CreateLectureCommand(
            actor=actor,
            section_id=section_id,
            title=request.title,
            content=request.content,
            position=request.position,
        )
    )
    return LectureResponse.model_validate(result)


@router.put(
    "/lectures/{lecture_id}",
    response_model=LectureResponse,
    summary="Update lecture",
    description="Updates a lecture if it belongs to a course managed by the current user.",
    responses={
        400: {
            "description": "Domain or application validation error.",
            "model": ErrorResponse,
        },
        404: {
            "description": "Lecture was not found.",
            "model": ErrorResponse,
        },
    },
)
async def update_lecture(
    lecture_id: UUID,
    request: UpdateLectureRequest,
    actor: User = Depends(get_current_author_or_admin),
    use_case: UpdateLectureUseCase = Depends(get_update_lecture_use_case),
) -> LectureResponse:
    result = await use_case.execute(
        UpdateLectureCommand(
            actor=actor,
            lecture_id=lecture_id,
            title=request.title,
            content=request.content,
            position=request.position,
        )
    )
    return LectureResponse.model_validate(result)


@router.delete(
    "/lectures/{lecture_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete lecture",
    description="Deletes a lecture from a course managed by the current user.",
    responses={
        404: {
            "description": "Lecture was not found.",
            "model": ErrorResponse,
        },
    },
)
async def delete_lecture(
    lecture_id: UUID,
    actor: User = Depends(get_current_author_or_admin),
    use_case: DeleteLectureUseCase = Depends(get_delete_lecture_use_case),
) -> Response:
    await use_case.execute(
        DeleteLectureCommand(
            actor=actor,
            lecture_id=lecture_id,
        )
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post(
    '/courses/{course_id}/publish',
    response_model=CourseResponse,
    summary='Publish course',
    description='Publishes the course if it is complete and ready for students.',
    responses={
        400: {
            'description': 'Course is not ready for publication.',
            'model': CoursePublicationErrorResponse,
        },
        404: {
            'description': 'Course was not found.',
            'model': ErrorResponse,
        },
    },
)
async def publish_course(
    course_id: UUID,
    actor: User = Depends(get_current_author_or_admin),
    use_case: PublishCourseUseCase = Depends(get_publish_course_use_case),
) -> CourseResponse:
    result = await use_case.execute(
        PublishCourseCommand(
            actor=actor,
            course_id=course_id,
        )
    )
    return CourseResponse.model_validate(result)

@router.post(
    '/courses/{course_id}/archive',
    response_model=CourseResponse,
    summary='Archive course',
    description='Removes the course from public visibility without deleting it.',
    responses={
        400: {
            'description': 'Domain or application validation error.',
            'model': ErrorResponse,
        },
        404: {
            'description': 'Course was not found.',
            'model': ErrorResponse,
        },
    },
)
async def archive_course(
    course_id: UUID,
    actor: User = Depends(get_current_author_or_admin),
    use_case: ArchiveCourseUseCase = Depends(get_archive_course_use_case),
) -> CourseResponse:
    result = await use_case.execute(
        ArchiveCourseCommand(
            actor=actor,
            course_id=course_id,
        )
    )
    return CourseResponse.model_validate(result)

@router.get(
    '/courses/{course_id}/publication-readiness',
    response_model=CoursePublicationReadinessResponse,
    summary='Get course publication readiness',
    description='Returns diagnostics that explain whether the course can be published.',
    responses={
        404: {
            'description': 'Course was not found.',
            'model': ErrorResponse,
        },
    },
)
async def get_course_publication_readiness(
    course_id: UUID,
    actor: User = Depends(get_current_author_or_admin),
    use_case: GetCoursePublicationReadinessUseCase = Depends(
        get_get_course_publication_readiness_use_case
    ),
) -> CoursePublicationReadinessResponse:
    result = await use_case.execute(
        GetCoursePublicationReadinessQuery(
            actor=actor,
            course_id=course_id,
        )
    )
    return CoursePublicationReadinessResponse.model_validate(result)

@router.post(
    "/courses/{course_id}/cover",
    response_model=CourseResponse,
    summary="Upload course cover",
    description="Uploads a cover image for a course and updates its cover_image_url.",
    responses={
        400: {
            "description": "Validation error or invalid cover file.",
            "model": ErrorResponse,
        },
        404: {
            "description": "Course was not found.",
            "model": ErrorResponse,
        },
    },
)
async def upload_course_cover(
    course_id : UUID,
    file : UploadFile = File(...),
    actor : User = Depends(get_current_author_or_admin),
    use_case : UploadCourseCoverUseCase = Depends(get_upload_course_cover_use_case),
) -> CourseResponse:
    content = await file.read()
    result = await use_case.execute(
        UploadCourseCoverCommand(
            actor=actor,
            course_id=course_id,
            file_name=file.filename or "cover.jpg",
            content=content,
            content_type=file.content_type or "",
        )
    )
    return CourseResponse.model_validate(result)
