class ApplicationError(Exception):
    default_message : str = "Application_error"
    status_code : str = "APPLICATION_ERROR"
    def __init__(self, message : str | None = None):
        self.message = message or self.default_message
        super().__init__(self.message)

class UnauthorizedError(ApplicationError):
    default_message : str = "Unauthorized_error"
    code : str = "UNAUTHORIZED_ERROR"

class ForbiddenError(ApplicationError):
    default_message : str = "Forbidden_error"
    code : str = "FORBIDDEN_ERROR"

class ConflictError(ApplicationError):
    default_message : str = "Conflict_error"
    code : str = "CONFLICT_ERROR"
