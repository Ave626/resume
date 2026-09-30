from app.presentation.api.schemas.auth import (
    CurrentUserResponse,
    LoginRequest,
    RegisteredUserResponse,
    RegisterUserRequest,
    TokenResponse,
)
from app.presentation.api.schemas.author_analytics import (
    AuthorCourseAnalyticsResponse,
    AuthorModuleAnalyticsResponse,
    DifficultQuestionAnalyticsResponse,
    DifficultTaskAnalyticsResponse,
    ProblematicCodeTaskAnalyticsResponse,
)
from app.presentation.api.schemas.catalog import (
    CourseCatalogCardResponse,
    CourseCatalogCountersResponse,
    CourseCatalogItemResponse,
    CourseCatalogModulePreviewResponse,
    CourseCatalogSectionPreviewResponse,
    CourseRatingSummaryResponse,
)
from app.presentation.api.schemas.code_submissions import (
    CodeSubmissionResponse,
    SubmitCodeSubmissionRequest,
)
from app.presentation.api.schemas.code_tasks import (
    CodeTaskResponse,
    CreateCodeTaskRequest,
    UpdateCodeTaskRequest,
)
from app.presentation.api.schemas.content import (
    AnswerOptionDetailsResponse,
    CodeTaskDetailsResponse,
    CodeTaskStructureResponse,
    CourseListItemResponse,
    CourseResponse,
    CourseStructureResponse,
    LectureResponse,
    LectureStructureResponse,
    ModuleStructureResponse,
    QuestionDetailsResponse,
    SectionStructureResponse,
    TaskDetailsResponse,
    TaskStructureResponse,
)
from app.presentation.api.schemas.course_publication import (
    CoursePublicationErrorResponse,
    CoursePublicationIssueResponse,
    CoursePublicationReadinessResponse,
)
from app.presentation.api.schemas.course_reviews import (
    CourseReviewResponse,
    UpsertCourseReviewRequest,
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
from app.presentation.api.schemas.profile import (
    UpdateMyProfileRequest,
    UserProfileResponse,
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
from app.presentation.api.schemas.student_analytics import (
    StudentCourseAnalyticsResponse,
    StudentModuleAnalyticsResponse,
    StudentWeakCodeTaskResponse,
    StudentWeakQuestionResponse,
    StudentWeakTaskResponse,
)
from app.presentation.api.schemas.task_attempts import (
    SubmitTaskAnswerRequest,
    TaskAttemptResponse,
)
from app.presentation.api.schemas.tasks import (
    CreateTaskRequest,
    TaskResponse,
    UpdateTaskRequest,
)
from app.presentation.api.schemas.test_cases import (
    CreateTestCaseRequest,
    TestCaseResponse,
    UpdateTestCaseRequest,
)

__all__ = [
    "AnswerOptionDetailsResponse",
    "AnswerOptionResponse",
    "AuthorCourseAnalyticsResponse",
    "AuthorModuleAnalyticsResponse",
    "CodeSubmissionResponse",
    "CodeTaskDetailsResponse",
    "CodeTaskResponse",
    "CodeTaskStructureResponse",
    "CourseCatalogCardResponse",
    "CourseCatalogCountersResponse",
    "CourseCatalogItemResponse",
    "CourseCatalogModulePreviewResponse",
    "CourseCatalogSectionPreviewResponse",
    "CourseListItemResponse",
    "CoursePublicationErrorResponse",
    "CoursePublicationIssueResponse",
    "CoursePublicationReadinessResponse",
    "CourseRatingSummaryResponse",
    "CourseResponse",
    "CourseReviewResponse",
    "CourseStructureResponse",
    "CreateAnswerOptionRequest",
    "CreateCodeTaskRequest",
    "CreateCourseRequest",
    "CreateLectureRequest",
    "CreateModuleRequest",
    "CreateQuestionRequest",
    "CreateSectionRequest",
    "CreateTaskRequest",
    "CreateTestCaseRequest",
    "CurrentUserResponse",
    "DifficultQuestionAnalyticsResponse",
    "DifficultTaskAnalyticsResponse",
    "ErrorResponse",
    "LectureResponse",
    "LectureStructureResponse",
    "LoginRequest",
    "ModuleResponse",
    "ModuleStructureResponse",
    "ProblematicCodeTaskAnalyticsResponse",
    "QuestionAttemptResultResponse",
    "QuestionDetailsResponse",
    "QuestionResponse",
    "RegisterUserRequest",
    "RegisteredUserResponse",
    "SectionResponse",
    "SectionStructureResponse",
    "StartQuestionAttemptResponse",
    "StudentCourseAnalyticsResponse",
    "StudentModuleAnalyticsResponse",
    "StudentWeakCodeTaskResponse",
    "StudentWeakQuestionResponse",
    "StudentWeakTaskResponse",
    "SubmitCodeSubmissionRequest",
    "SubmitQuestionAnswerRequest",
    "SubmitTaskAnswerRequest",
    "TaskAttemptResponse",
    "TaskDetailsResponse",
    "TaskResponse",
    "TaskStructureResponse",
    "TestCaseResponse",
    "TokenResponse",
    "UpdateAnswerOptionRequest",
    "UpdateCodeTaskRequest",
    "UpdateCourseRequest",
    "UpdateLectureRequest",
    "UpdateModuleRequest",
    "UpdateMyProfileRequest",
    "UpdateQuestionRequest",
    "UpdateSectionRequest",
    "UpdateTaskRequest",
    "UpdateTestCaseRequest",
    "UpsertCourseReviewRequest",
    "UserProfileResponse",
]
