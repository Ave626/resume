from abc import ABC, abstractmethod
from app.domain.entities import CodeSubmission, CodeTask, ExecutionResult, TestCase


class CodeExecutionGateway(ABC):
    @abstractmethod
    async def execute(
        self,
        code_task: CodeTask,
        submission: CodeSubmission,
        test_cases: list[TestCase],
    ) -> ExecutionResult:
        raise NotImplementedError
