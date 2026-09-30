import os
from dataclasses import dataclass
from uuid import UUID, uuid4

from app.application.exceptions import InvalidCourseCoverFileError
from app.application.interfaces.services.file_storage import FileStorage
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.course import Course
from app.domain.entities.user import User

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024


@dataclass(slots=True)
class UploadCourseCoverCommand:
    actor: User
    course_id: UUID
    file_name: str
    content: bytes
    content_type: str


class UploadCourseCoverUseCase:
    def __init__(self, uow: UnitOfWork, file_storage: FileStorage) -> None:
        self.uow = uow
        self.file_storage = file_storage
        self.course_access_service = CourseAccessService(uow=uow)

    async def execute(self, command: UploadCourseCoverCommand) -> Course:
        self._validate_file(command)

        async with self.uow:
            course = await self.course_access_service.ensure_can_manage_course(
                actor=command.actor,
                course_id=command.course_id,
            )

            _, ext = os.path.splitext(command.file_name)
            storage_key = f"covers/{course.id}_{uuid4().hex[:8]}{ext.lower()}"

            cover_url = await self.file_storage.upload(
                file_name=storage_key,
                content=command.content,
                content_type=command.content_type.lower(),
            )

            course.update_metadata(
                cover_image_url=cover_url,
                short_description=course.short_description,
                difficulty=course.difficulty,
                tag_names=course.tag_names,
            )
            await self.uow.courses.update(course)
            await self.uow.commit()
            return course

    def _validate_file(self, command: UploadCourseCoverCommand) -> None:
        if not command.content:
            raise InvalidCourseCoverFileError("File is empty.")

        if len(command.content) > MAX_FILE_SIZE_BYTES:
            raise InvalidCourseCoverFileError("File size exceeds 5 MB limit.")

        content_type = (command.content_type or "").lower()
        if content_type not in ALLOWED_CONTENT_TYPES:
            raise InvalidCourseCoverFileError(
                f"Unsupported content type '{content_type}'. Allowed: jpeg, png, webp."
            )

        _, ext = os.path.splitext(command.file_name)
        if ext.lower() not in ALLOWED_EXTENSIONS:
            raise InvalidCourseCoverFileError(
                f"Unsupported file extension '{ext}'. Allowed: .jpg, .jpeg, .png, .webp."
            )
