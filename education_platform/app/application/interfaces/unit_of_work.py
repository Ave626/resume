from abc import ABC, abstractmethod

from app.application.interfaces.repositories import (
    AnswerOptionRepository,
    CourseRepository,
    LectureRepository,
    ModuleRepository,
    QuestionAttemptRepository,
    QuestionRepository,
    SectionRepository,
    UserRepository,
)


class UnitOfWork(ABC):
    courses: CourseRepository
    modules: ModuleRepository
    sections: SectionRepository
    lectures: LectureRepository
    users: UserRepository
    questions: QuestionRepository
    answer_options: AnswerOptionRepository
    question_attempts: QuestionAttemptRepository

    @abstractmethod
    async def __aenter__(self) -> "UnitOfWork":
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, exc_type, exc, tb) -> None:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError
