class DomainError(Exception):
    pass

class InvalidCourseError(DomainError):
    pass

class InvalidModuleError(DomainError):
    pass

class InvalidSectionError(DomainError):
    pass

class InvalidLectureError(DomainError):
    pass

class InvalidUserError(DomainError):
    pass
