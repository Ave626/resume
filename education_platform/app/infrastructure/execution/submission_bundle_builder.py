from abc import abstractmethod,ABC
from dataclasses import dataclass
from tempfile import TemporaryDirectory
from pathlib import Path

from app.domain.entities.code_submission import CodeSubmission
from app.domain.entities.test_case import TestCase

@dataclass(slots=True)
class ExecutionBundle:
    directory : Path
    command : list[str]

class SubmissionBundleBuilder(ABC):
    @abstractmethod
    def build(
        self,
        submission : CodeSubmission,
        test_cases : list[TestCase]
    ) -> tuple[TemporaryDirectory,ExecutionBundle]:
        raise NotImplementedError