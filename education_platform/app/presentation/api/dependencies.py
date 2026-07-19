from collections.abc import AsyncGenerator
from fastapi import Depends, Security
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from app.domain.entities.user import User
from app.infrastructure.security.jwt_token_service import InvalidTokenError
from app.presentation.exceptions import AuthenticationError
from app.application.use_cases.courses.get_course import GetCourseUseCase
from app.application.use_cases.courses.get_course_structure import GetCourseStructureUseCase
from app.application.use_cases.courses.get_courses import GetCoursesUseCase
from app.application.use_cases.lectures.get_lecture import GetLectureUseCase
from app.application.use_cases.courses.create_course import CreateCourseUseCase
from app.application.use_cases.courses.update_course import UpdateCourseUseCase
from app.application.use_cases.lectures.create_lecture import CreateLectureUseCase
from app.application.use_cases.lectures.update_lecture import UpdateLectureUseCase
from app.application.use_cases.modules.create_module import CreateModuleUseCase
from app.application.use_cases.modules.update_module import UpdateModuleUseCase
from app.application.use_cases.sections.create_section import CreateSectionUseCase
from app.application.use_cases.sections.update_section import UpdateSectionUseCase
from app.application.use_cases.lectures.delete_lecture import DeleteLectureUseCase
from app.application.use_cases.modules.delete_module import DeleteModuleUseCase
from app.application.use_cases.sections.delete_section import DeleteSectionUseCase
from app.application.use_cases.courses.delete_course import DeleteCourseUseCase
from app.application.interfaces.services.password_hasher import PasswordHasher
from app.application.use_cases.auth.register_user import RegisterUserUseCase
from app.infrastructure.security.password_hasher import PwdlibPasswordHasher
from app.application.use_cases.auth.login_user import LoginUserUseCase
from app.application.interfaces.services.token_service import TokenService
from app.infrastructure.security.jwt_token_service import JwtTokenService
from app.infrastructure.database import SessionFactory, SqlAlchemyUnitOfWork
from app.presentation.exceptions import PermissionDeniedError

http_bearer = HTTPBearer(auto_error=False)


def get_token_service() -> TokenService:
    return JwtTokenService()
    
async def get_uow() -> AsyncGenerator[SqlAlchemyUnitOfWork]:
    async with SqlAlchemyUnitOfWork(session_factory=SessionFactory) as uow:
        yield uow

def get_get_courses_use_case(uow : SqlAlchemyUnitOfWork = Depends(get_uow)) -> GetCoursesUseCase:
    return GetCoursesUseCase(course_repository=uow.courses)

def get_get_course_use_case(
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),) -> GetCourseUseCase:
    return GetCourseUseCase(course_repository=uow.courses)

def get_get_course_structure_use_case(
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> GetCourseStructureUseCase:
    return GetCourseStructureUseCase(
        course_repository=uow.courses,
        module_repository=uow.modules,
        section_repository=uow.sections,
        lecture_repository=uow.lectures,
    )

def get_get_lecture_use_case(
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> GetLectureUseCase:
    return GetLectureUseCase(lecture_repository=uow.lectures)


def get_create_course_use_case() -> CreateCourseUseCase:
    return CreateCourseUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )

def get_update_course_use_case() -> UpdateCourseUseCase:
    return UpdateCourseUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )

def get_create_module_use_case() -> CreateModuleUseCase:
    return CreateModuleUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )

def get_update_module_use_case() -> UpdateModuleUseCase:
    return UpdateModuleUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )

def get_create_section_use_case() -> CreateSectionUseCase:
    return CreateSectionUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )

def get_update_section_use_case() -> UpdateSectionUseCase:
    return UpdateSectionUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )

def get_create_lecture_use_case() -> CreateLectureUseCase:
    return CreateLectureUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )

def get_update_lecture_use_case() -> UpdateLectureUseCase:
    return UpdateLectureUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )

def get_delete_lecture_use_case() -> DeleteLectureUseCase:
    return DeleteLectureUseCase(
        uow = SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )

def get_delete_section_use_case() -> DeleteSectionUseCase:
    return DeleteSectionUseCase(
        uow = SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )

def get_delete_module_use_case() -> DeleteModuleUseCase:
    return DeleteModuleUseCase(
        uow = SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )

def get_delete_course_use_case() -> DeleteCourseUseCase:
    return DeleteCourseUseCase(
        uow = SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )

def get_password_hasher() -> PasswordHasher:
    return PwdlibPasswordHasher()

def get_register_user_use_case() -> RegisterUserUseCase:
    return RegisterUserUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory),
        password_hasher=get_password_hasher(),
    )

def get_login_user_use_case() -> LoginUserUseCase:
    return LoginUserUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory),
        password_hasher=get_password_hasher(),
        token_service=get_token_service(),
    )


async def get_current_user(
    credentials : HTTPAuthorizationCredentials | None = Security(http_bearer),
    uow : SqlAlchemyUnitOfWork = Depends(get_uow),
    token_serice : TokenService = Depends(get_token_service),
) -> User:
    if credentials is None:
        raise AuthenticationError("Auth credentials were not provided")
    if credentials.scheme.lower() != "bearer":
        raise AuthenticationError("Auth scheme must be bearer")
    try:
        user_id = token_serice.get_user_id(credentials.credentials)
    except InvalidTokenError as exc:
        raise AuthenticationError(str(exc)) from exc
    
    user = await uow.users.get_by_id(user_id)
    if user is None:
        raise AuthenticationError("User from token was not found")
    return user

async def get_current_admin(current_user : User = Depends(get_current_user)) -> User:
    if not current_user.can_manage_platform():
        raise PermissionDeniedError("Admin access is required")
    return current_user

