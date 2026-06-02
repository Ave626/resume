class ApplicationError(Exception):
    pass

class CourseNotFoundError(ApplicationError):
    pass

class LectureNotFoundError(ApplicationError):
    pass

