from app.presentation.api.schemas.auth import (
    CurrentUserResponse,
    LoginRequest,
    RegisteredUserResponse,
    RegisterUserRequest,
    TokenResponse,
)
from app.presentation.api.schemas.content import (
    CourseListItemResponse,
    CourseResponse,
    CourseStructureResponse,
    LectureResponse,
    LectureStructureResponse,
    ModuleStructureResponse,
    SectionStructureResponse,
)
from app.presentation.api.schemas.courses import (
    CreateCourseRequest,
    UpdateCourseRequest,
)
from app.presentation.api.schemas.errors import ErrorResponse
from app.presentation.api.schemas.lectures import (
    CreateLectureRequest,
    UpdateLectureRequest,
)
from app.presentation.api.schemas.modules import (
    CreateModuleRequest,
    ModuleResponse,
    UpdateModuleRequest,
)
from app.presentation.api.schemas.question_attempts import (
    QuestionAttemptResultResponse,
    StartQuestionAttemptResponse,
    SubmitQuestionAnswerRequest,
)
from app.presentation.api.schemas.questions import (
    AnswerOptionResponse,
    CreateAnswerOptionRequest,
    CreateQuestionRequest,
    QuestionResponse,
    UpdateAnswerOptionRequest,
    UpdateQuestionRequest,
)
from app.presentation.api.schemas.sections import (
    CreateSectionRequest,
    SectionResponse,
    UpdateSectionRequest,
)

__all__ = [
    "AnswerOptionResponse",
    "CourseListItemResponse",
    "CourseResponse",
    "CourseStructureResponse",
    "CreateAnswerOptionRequest",
    "CreateCourseRequest",
    "CreateLectureRequest",
    "CreateModuleRequest",
    "CreateQuestionRequest",
    "CreateSectionRequest",
    "CurrentUserResponse",
    "ErrorResponse",
    "LectureResponse",
    "LectureStructureResponse",
    "LoginRequest",
    "ModuleResponse",
    "ModuleStructureResponse",
    "QuestionAttemptResultResponse",
    "QuestionResponse",
    "RegisterUserRequest",
    "RegisteredUserResponse",
    "SectionResponse",
    "SectionStructureResponse",
    "StartQuestionAttemptResponse",
    "SubmitQuestionAnswerRequest",
    "TokenResponse",
    "UpdateAnswerOptionRequest",
    "UpdateCourseRequest",
    "UpdateLectureRequest",
    "UpdateModuleRequest",
    "UpdateQuestionRequest",
    "UpdateSectionRequest",
]
