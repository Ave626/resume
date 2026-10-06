from app.domain.entities.answer_option import AnswerOption
from app.domain.entities.code_submission import CodeSubmission, CodeSubmissionStatus
from app.domain.entities.code_task import CodeTask, CodeTaskLanguage
from app.domain.entities.comment import Comment
from app.domain.entities.course import Course
from app.domain.entities.course_review import CourseReview
from app.domain.entities.execution_result import ExecutionResult, ExecutionStatus
from app.domain.entities.lecture import Lecture
from app.domain.entities.module import Module
from app.domain.entities.progress import Progress
from app.domain.entities.question import Question, QuestionType
from app.domain.entities.question_attempt import QuestionAttempt, QuestionResultStatus
from app.domain.entities.section import Section
from app.domain.entities.student_activity import StudentActivity, StudentActivityType
from app.domain.entities.task import Task, TaskCheckType
from app.domain.entities.task_attempt import TaskAttempt, TaskAttemptStatus
from app.domain.entities.test_case import TestCase
from app.domain.entities.user import User, UserRole

__all__ = [
    "AnswerOption",
    "CodeSubmission",
    "CodeSubmissionStatus",
    "CodeTask",
    "CodeTaskLanguage",
    "Comment",
    "Course",
    "CourseReview",
    "ExecutionResult",
    "ExecutionStatus",
    "Lecture",
    "Module",
    "Progress",
    "Question",
    "QuestionAttempt",
    "QuestionResultStatus",
    "QuestionType",
    "Section",
    "StudentActivity",
    "StudentActivityType",
    "Task",
    "TaskAttempt",
    "TaskAttemptStatus",
    "TaskCheckType",
    "TestCase",
    "User",
    "UserRole",
]
