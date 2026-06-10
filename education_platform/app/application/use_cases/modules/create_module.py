from dataclasses import dataclass
from uuid import UUID,uuid4
from app.domain.entities.module import Module
from app.application.exceptions import CourseNotFoundError
from app.application.interfaces.unit_of_work import UnitOfWork

@dataclass(slots=True)
class CreateModuleCommand:
    course_id : UUID
    title : str
    description : str
    position : int

class CreateModuleUseCase:
    def __init__(self,uow : UnitOfWork) ->  None:
        self.uow = uow
    
    async def execute(self,command : CreateModuleCommand) -> Module:
        async with self.uow:
            course = await self.uow.courses.get_by_id(command.course_id)
            if course is None:
                raise CourseNotFoundError("Такого курса нет")
            module = Module(
                id = uuid4(),
                course_id=course.id,
                title = command.title,
                description=command.description,
                position=command.position
            )
            course.module_ids.append(module.id)
            await self.uow.modules.add(module)
            await self.uow.courses.update(course)
            await self.uow.commit()
            return module
